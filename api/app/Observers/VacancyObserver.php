<?php

namespace App\Observers;

use App\Models\Vacancy;

class VacancyObserver
{
    public function updating(Vacancy $vacancy): void
    {
        if ($vacancy->isDirty('status')) {
            $vacancy->status_changed_at = now();
        }
    }
}