<?php

namespace App\Observers;

use App\Models\Vacancy;
use App\Models\VacancyStatusHistory;

class VacancyObserver
{
    public function updating(Vacancy $vacancy): void
    {
        if ($vacancy->isDirty('status')) {
            $vacancy->status_changed_at = now();
        }
    }

    public function updated(Vacancy $vacancy): void
    {
        if ($vacancy->wasChanged('status')) {
            VacancyStatusHistory::create([
                'vacancy_id' => $vacancy->id,
                'status'     => $vacancy->status,
            ]);
        }
    }
}