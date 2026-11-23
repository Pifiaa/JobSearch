<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('vacancies', function (Blueprint $table) {
            $table->boolean('vacante_coherente')->nullable()->after('llm_detail');
            $table->jsonb('coherence_detail')->nullable()->after('vacante_coherente');
        });
    }

    public function down(): void
    {
        Schema::table('vacancies', function (Blueprint $table) {
            $table->dropColumn(['vacante_coherente', 'coherence_detail']);
        });
    }
};
