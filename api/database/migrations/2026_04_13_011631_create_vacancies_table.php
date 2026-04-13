<?php

use App\Enums\VacancyModality;
use App\Enums\VacancyStatus;
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('vacancies', function (Blueprint $table) {
            $table->id();
            $table->string('external_id');
            $table->string('title');
            $table->string('company')->nullable();
            $table->string('city')->nullable();
            $table->string('department')->nullable();
            $table->string('country')->nullable();
            $table->enum('modality', array_column(VacancyModality::cases(), 'value'))->nullable();
            $table->string('salary_range')->nullable();
            $table->text('description')->nullable();
            $table->string('description_hash', 32)->nullable()->index();
            $table->text('url');
            $table->boolean('is_active')->default(true);
            $table->integer('cv_score')->nullable();
            $table->float('cv_score_semantic')->nullable();
            $table->jsonb('cv_keywords_detail')->nullable();
            $table->enum('status', array_column(VacancyStatus::cases(), 'value'))->default(VacancyStatus::Nueva->value);
            $table->timestamp('published_at')->nullable();
            $table->timestamp('scraped_at')->useCurrent();
            $table->timestamps();
            $table->unique(['source_id', 'external_id']);
            $table->foreignId('source_id')->constrained('sources')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('vacancies');
    }
};
