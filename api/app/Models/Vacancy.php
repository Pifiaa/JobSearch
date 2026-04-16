<?php

namespace App\Models;

use App\Enums\VacancyModality;
use App\Enums\VacancyStatus;
use App\Observers\VacancyObserver;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Attributes\ObservedBy;
use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Table('vacancies')]
#[ObservedBy(VacancyObserver::class)]
#[Fillable([
    'source_id',
    'external_id',
    'title',
    'company',
    'city',
    'department',
    'country',
    'modality',
    'salary_range',
    'description',
    'description_hash',
    'url',
    'is_active',
    'cv_score',
    'cv_score_semantic',
    'cv_keywords_detail',
    'status',
    'status_changed_at',
    'published_at',
    'scraped_at',
])]
class Vacancy extends Model
{
    protected $casts = [
        'modality'           => VacancyModality::class,
        'status'             => VacancyStatus::class,
        'cv_keywords_detail' => 'array',
        'is_active'          => 'boolean',
        'published_at'       => 'datetime',
        'scraped_at'         => 'datetime',
        'status_changed_at'  => 'datetime',
    ];

    public function source(): BelongsTo
    {
        return $this->belongsTo(Source::class);
    }

    public function statusHistory(): HasMany
    {
        return $this->hasMany(VacancyStatusHistory::class)->orderBy('changed_at', 'asc');
    }
}