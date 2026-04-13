<?php

namespace App\Enums;

enum VacancyStatus: string
{
    case Nueva = 'nueva';
    case Guardada = 'guardada';
    case Postulada = 'postulada';
    case Descartada = 'descartada';
    case Observada = 'observada';
}