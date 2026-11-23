<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @page { margin: 40px 45px; }
        body {
            font-family: 'DejaVu Sans', sans-serif;
            color: #1f2937;
            font-size: 12px;
            line-height: 1.5;
        }
        h1 {
            font-size: 18px;
            margin: 0 0 4px 0;
            color: #1e3a8a;
        }
        .subtitle {
            font-size: 11px;
            color: #6b7280;
            margin-bottom: 20px;
        }
        h2 {
            font-size: 13px;
            color: #1e3a8a;
            border-bottom: 1px solid #dbeafe;
            padding-bottom: 3px;
            margin-top: 18px;
            margin-bottom: 8px;
        }
        p { margin: 0 0 8px 0; }
        ul { margin: 0; padding-left: 18px; }
        li { margin-bottom: 4px; }
        .skills span {
            display: inline-block;
            background: #eff6ff;
            color: #1e3a8a;
            border: 1px solid #dbeafe;
            border-radius: 10px;
            padding: 2px 8px;
            margin: 2px 4px 2px 0;
            font-size: 10px;
        }
        .footer-note {
            margin-top: 24px;
            font-size: 9px;
            color: #9ca3af;
        }
    </style>
</head>
<body>
    <h1>CV adaptado — {{ $vacancy->title }}</h1>
    <div class="subtitle">{{ $vacancy->company ?? 'Empresa no especificada' }} · Generado el {{ now()->format('d/m/Y') }}</div>

    <h2>Resumen profesional</h2>
    <p>{{ $data['resumen_profesional'] ?? '' }}</p>

    @if(!empty($data['habilidades_destacadas']))
        <h2>Habilidades destacadas para esta vacante</h2>
        <div class="skills">
            @foreach($data['habilidades_destacadas'] as $skill)
                <span>{{ $skill }}</span>
            @endforeach
        </div>
    @endif

    @if(!empty($data['sugerencias_bullets']))
        <h2>Puntos a resaltar en la entrevista</h2>
        <ul>
            @foreach($data['sugerencias_bullets'] as $bullet)
                <li>{{ $bullet }}</li>
            @endforeach
        </ul>
    @endif

    <div class="footer-note">
        Portada generada automáticamente a partir del CV original. El detalle completo de experiencia
        se encuentra en las páginas siguientes.
    </div>
</body>
</html>
