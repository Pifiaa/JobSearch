<?php

namespace Database\Seeders;

use App\Models\Source;
use Illuminate\Database\Seeder;

class SourceSeeder extends Seeder
{
    public function run(): void
    {
        $sources = [
            [
                'name'       => 'computrabajo',
                'url'        => 'https://co.computrabajo.com',
                'is_active'  => true,
                'rate_limit' => 0,
                'headers'    => [
                    'queries' => [
                        'desarrollador',
                        'programador',
                        'ingeniero de software',
                        'dev',
                    ],
                    'blacklist' => ['bairesdev'],
                ],
            ],
            [
                'name'       => 'ticjob',
                'url'        => 'https://ticjob.co',
                'is_active'  => true,
                'rate_limit' => 0,
                'headers'    => [
                    'blacklist' => ['bairesdev'],
                ],
            ],
            [
                'name'       => 'elempleo',
                'url'        => 'https://www.elempleo.com',
                'is_active'  => true,
                'rate_limit' => 3,
                'headers'    => [
                    'queries'   => ['desarrollador', 'programador', 'ingeniero-de-software', 'developer'],
                    'blacklist' => ['bairesdev'],
                ],
            ],
        ];

        foreach ($sources as $data) {
            Source::updateOrCreate(
                ['name' => $data['name']],
                ['url' => $data['url']],
                $data
            );
        }
    }
}