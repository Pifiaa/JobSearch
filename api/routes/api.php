<?php

use App\Http\Controllers\AnalyticsController;
use App\Http\Controllers\ScraperController;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\VacancyController;
use App\Http\Controllers\CompanyBlacklistController;
use App\Http\Controllers\CvController;
use App\Http\Controllers\CvTailorController;

Route::get('/vacancies',               [VacancyController::class, 'index']);
Route::patch('/vacancies/{id}/status', [VacancyController::class, 'updateStatus']);
Route::get('/vacancies/{id}/status-history', [VacancyController::class, 'statusHistory']);

Route::post('/scraper/run/all', [ScraperController::class, 'runAll']);
Route::post('/scraper/run/{sourceId}', [ScraperController::class, 'run']);

Route::prefix('analytics')->controller(AnalyticsController::class)->group(function () {
    Route::get('summary',         'summary');
    Route::get('skills',          'skills');
    Route::get('companies',       'companies');
    Route::get('salaries',        'salaries');
    Route::get('status-timeline', 'statusTimeline');
});

Route::get('/cv/info',     [CvController::class, 'info']);
Route::post('/cv/upload',  [CvController::class, 'upload']);

// CV a medida: se ejecuta únicamente bajo demanda desde el frontend, sin cron ni cola.
Route::post('/vacancies/{id}/tailor-cv',     [CvTailorController::class, 'generate']);
Route::get('/vacancies/{id}/tailor-cv/pdf',  [CvTailorController::class, 'exportPdf']);
Route::get('/vacancies/{id}/tailor-cv/brief', [CvTailorController::class, 'exportBrief']);

Route::post('/companies/blacklist', [CompanyBlacklistController::class, 'store']);
