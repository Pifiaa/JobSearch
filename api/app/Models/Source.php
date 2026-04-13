<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use App\Models\Vacancy;

#[Table('sources')]
#[Fillable([
    'name',
    'url',
    'headers',
    'rate_limit',
    'is_active',
    'need_auth',
    'last_executed_at',
])]
class Source extends Model
{
    protected $casts = [
        'headers' => 'array',
        'is_active' => 'boolean',
        'need_auth' => 'boolean',
        'last_executed_at' => 'datetime',
    ];

    public function vacancies(): HasMany
    {
        return $this->hasMany(Vacancy::class);
    }
}
