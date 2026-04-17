<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        DB::statement('ALTER TABLE vacancies DROP CONSTRAINT IF EXISTS vacancies_status_check');
        DB::statement("ALTER TABLE vacancies ADD CONSTRAINT vacancies_status_check CHECK (status IN ('nueva', 'guardada', 'postulada', 'descartada', 'observada', 'no_idoneo'))");
    }

    public function down(): void
    {
        DB::statement('ALTER TABLE vacancies DROP CONSTRAINT IF EXISTS vacancies_status_check');
        DB::statement("ALTER TABLE vacancies ADD CONSTRAINT vacancies_status_check CHECK (status IN ('nueva', 'guardada', 'postulada', 'descartada', 'observada'))");
    }
};