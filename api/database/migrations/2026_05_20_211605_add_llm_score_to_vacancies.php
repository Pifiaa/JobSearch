<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('vacancies', function (Blueprint $table) {
            $table->unsignedSmallInteger('llm_score')->nullable()->after('cv_score_semantic');
            $table->jsonb('llm_detail')->nullable()->after('llm_score');
        });
    }

    public function down(): void
    {
        Schema::table('vacancies', function (Blueprint $table) {
            $table->dropColumn(['llm_score', 'llm_detail']);
        });
    }
};
