<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class VacancyStatusHistory extends Model
{
    protected $table = 'vacancy_status_history';
    public $timestamps = false;

    protected $fillable = [
        'vacancy_id',
        'status',
        'changed_at',
    ];

    protected $casts = [
        'changed_at' => 'datetime',
    ];

    public function vacancy()
    {
        return $this->belongsTo(Vacancy::class);
    }
}