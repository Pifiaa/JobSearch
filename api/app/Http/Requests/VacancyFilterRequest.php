<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class VacancyFilterRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'source_id'  => ['nullable', 'integer', 'exists:sources,id'],
            'modality'   => ['nullable', 'string', 'in:presencial,hibrido,remoto_colombia,remoto_internacional'],
            'city'       => ['nullable', 'string', 'max:100'],
            'score_min'  => ['nullable', 'numeric', 'min:0', 'max:100'],
            'status'     => ['nullable', 'string', 'in:nueva,guardada,postulada,descartada,observada'],
            'search'     => ['nullable', 'string', 'max:200'],
            'sort'       => ['nullable', 'string', 'in:recent,score,company'],
            'per_page'   => ['nullable', 'integer', 'min:1', 'max:100'],
        ];
    }
}