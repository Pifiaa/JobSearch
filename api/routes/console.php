<?php

use Illuminate\Support\Facades\Schedule;

Schedule::command('scraper:run-all')->dailyAt('09:30');
Schedule::command('scraper:run-all')->dailyAt('13:30');
Schedule::command('scraper:run-all')->dailyAt('19:00');
Schedule::command('vacancies:clean-old')->dailyAt('12:00');