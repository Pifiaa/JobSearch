<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Model;

#[Table('company_blacklist')]
#[Fillable([
    'name',
    'reason',
])]
class CompanyBlacklist extends Model
{
    //
}
