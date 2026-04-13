<?php

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
        Schema::create('sources', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->text('url');
            $table->json('headers')->nullable();
            $table->integer('rate_limit')->default(0);
            $table->boolean('is_active')->default(true);
            $table->boolean('need_auth')->default(false);
            $table->timestamp('last_executed_at')->nullable();
            $table->timestamps();
            $table->unique('url');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('sources');
    }
};
