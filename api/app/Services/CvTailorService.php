<?php

namespace App\Services;

use App\Models\Vacancy;
use Barryvdh\DomPDF\Facade\Pdf;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\Log;
use setasign\Fpdi\Fpdi;

class CvTailorService
{
    private string $cvPath = '/home/dev/projects/jobsearch/worker/data/cv.pdf';

    /**
     * Dispara el worker Python (docker exec) para generar sugerencias de
     * adaptación del CV a una vacante puntual. Se ejecuta únicamente cuando
     * el usuario lo solicita explícitamente desde el frontend — no hay
     * scheduler ni job en cola detrás de este método.
     */
    public function tailor(Vacancy $vacancy): array
    {
        if (!$vacancy->description) {
            throw new \RuntimeException('La vacante no tiene descripción para adaptar el CV');
        }

        // La generación en GPUs de 6GB puede tardar 1-3 minutos; no dejar que
        // el límite de ejecución de PHP corte la petición a mitad de camino.
        set_time_limit(0);

        $tmpFile = tempnam(sys_get_temp_dir(), 'tailor_') . '.json';
        file_put_contents($tmpFile, json_encode(['description' => $vacancy->description]));

        $cmd = sprintf(
            'docker exec -i jobsearch_worker sh -c %s < %s 2>/dev/null',
            escapeshellarg('cd /app && python tailor.py'),
            escapeshellarg($tmpFile)
        );

        $output = shell_exec($cmd);
        unlink($tmpFile);

        $data = json_decode($output ?? '', true);

        if (!$output || json_last_error() !== JSON_ERROR_NONE) {
            Log::error('CvTailorService: output inválido', ['raw' => substr($output ?? '', 0, 200)]);
            throw new \RuntimeException('El worker no devolvió un resultado válido');
        }

        if (!empty($data['error'])) {
            Log::warning('CvTailorService: worker respondió con error', ['error' => $data['error']]);
        }

        $vacancy->update([
            'tailored_cv'              => $data,
            'tailored_cv_generated_at' => now(),
        ]);

        return $data;
    }

    /**
     * Genera una portada adaptada en PDF y la fusiona delante del cv.pdf
     * original (el CV real no se toca ni se reescribe, solo se antepone
     * una página de resumen orientada a la vacante).
     */
    public function exportPdf(Vacancy $vacancy): Response
    {
        $this->ensureTailored($vacancy);

        if (!file_exists($this->cvPath)) {
            throw new \RuntimeException('No se encontró el CV original en el worker');
        }

        $coverHtml = view('pdf.cv-cover', [
            'data'    => $vacancy->tailored_cv,
            'vacancy' => $vacancy,
        ])->render();

        $coverPath = tempnam(sys_get_temp_dir(), 'cover_') . '.pdf';
        Pdf::loadHTML($coverHtml)->save($coverPath);

        $pdf = new Fpdi();
        foreach ([$coverPath, $this->cvPath] as $file) {
            $pageCount = $pdf->setSourceFile($file);
            for ($i = 1; $i <= $pageCount; $i++) {
                $tpl  = $pdf->importPage($i);
                $size = $pdf->getTemplateSize($tpl);
                $pdf->AddPage($size['orientation'], [$size['width'], $size['height']]);
                $pdf->useTemplate($tpl);
            }
        }

        unlink($coverPath);

        $filename = "cv_adaptado_{$vacancy->id}.pdf";

        return response($pdf->Output('S'), 200, [
            'Content-Type'        => 'application/pdf',
            'Content-Disposition' => "attachment; filename=\"$filename\"",
        ]);
    }

    /**
     * Genera un brief en Markdown, no un documento "bonito": pensado para
     * pegarse directo como contexto en otra IA (ChatGPT, Claude, etc.) junto
     * con el CV original, para que esa IA redacte el CV final.
     */
    public function exportBrief(Vacancy $vacancy): Response
    {
        $this->ensureTailored($vacancy);
        $data = $vacancy->tailored_cv;

        $lines = [];
        $lines[] = "# Brief para adaptar CV — {$vacancy->title}";
        $lines[] = ($vacancy->company ? "**Empresa:** {$vacancy->company}  " : null);
        $lines[] = "**Generado:** " . now()->format('Y-m-d');
        $lines[] = "";
        $lines[] = "## Instrucciones para la IA";
        $lines[] = "Usa este brief junto con mi CV original (adjunto aparte) para reescribir " .
                    "el resumen profesional y priorizar los logros más relevantes para esta " .
                    "vacante. No inventes experiencia, cargos, empresas ni tecnologías que no " .
                    "estén en mi CV real. Lo listado en \"Brechas\" es información que NO tengo " .
                    "y no debe agregarse como si la tuviera.";
        $lines[] = "";
        $lines[] = "## Descripción de la vacante";
        $lines[] = $vacancy->description ?: '(sin descripción)';
        $lines[] = "";
        $lines[] = "## Resumen profesional sugerido";
        $lines[] = $data['resumen_profesional'] ?: '(sin datos)';
        $lines[] = "";

        if (!empty($data['habilidades_destacadas'])) {
            $lines[] = "## Habilidades a priorizar";
            foreach ($data['habilidades_destacadas'] as $s) {
                $lines[] = "- {$s}";
            }
            $lines[] = "";
        }

        if (!empty($data['sugerencias_bullets'])) {
            $lines[] = "## Puntos a resaltar en logros/experiencia";
            foreach ($data['sugerencias_bullets'] as $b) {
                $lines[] = "- {$b}";
            }
            $lines[] = "";
        }

        if (!empty($data['brechas'])) {
            $lines[] = "## Brechas frente a esta vacante (NO tengo esto — no inventar)";
            foreach ($data['brechas'] as $b) {
                $lines[] = "- {$b}";
            }
            $lines[] = "";
        }

        $content  = implode("\n", array_filter($lines, fn($l) => $l !== null));
        $filename = "brief_cv_{$vacancy->id}.md";

        return response($content, 200, [
            'Content-Type'        => 'text/markdown; charset=utf-8',
            'Content-Disposition' => "attachment; filename=\"$filename\"",
        ]);
    }

    private function ensureTailored(Vacancy $vacancy): void
    {
        if (!$vacancy->tailored_cv) {
            throw new \RuntimeException('Genera primero el CV adaptado para esta vacante');
        }
    }
}
