<?php

namespace App\Enums;

enum VacancyModality: string
{
    case Presencial = 'presencial';
    case Hibrido = 'hibrido';
    case RemotoColombia = 'remoto_colombia';
    case RemotoInternacional = 'remoto_internacional';
}
