<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('vacancies', function (Blueprint $table) {
            $table->jsonb('tailored_cv')->nullable()->after('llm_detail');
            $table->timestamp('tailored_cv_generated_at')->nullable()->after('tailored_cv');
        });
    }

    public function down(): void
    {
        Schema::table('vacancies', function (Blueprint $table) {
            $table->dropColumn(['tailored_cv', 'tailored_cv_generated_at']);
        });
    }
};
