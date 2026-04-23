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
            [
                'name'       => 'getonboard',
                'url'        => 'https://www.getonbrd.com',
                'is_active'  => true,
                'rate_limit' => 1,
                'headers'    => [
                    'queries'   => ['desarrollador', 'programador', 'laravel', 'php', 'backend', 'fullstack'],
                    'blacklist' => ['bairesdev'],
                ],
            ],
            [
                'name'       => 'buscojobs',
                'url'        => 'https://www.buscojobs.com.co',
                'is_active'  => false,
                'rate_limit' => 3,
                'headers'    => [
                    'queries'   => ['desarrollador', 'programador', 'ingeniero-de-software', 'developer', 'backend', 'fullstack'],
                    'blacklist' => ['bairesdev'],
                ],
            ],
            [
                'name'       => 'magneto',
                'url'        => 'https://www.magneto365.com',
                'is_active'  => true,
                'rate_limit' => 2,
                'headers'    => [
                    'queries'   => ['desarrollador', 'programador', 'ingeniero-de-software', 'developer', 'backend', 'fullstack'],
                    'blacklist' => ['bairesdev'],
                ],
            ],
            [
                'name'       => 'sena',
                'url'        => 'https://agenciapublicadeempleo.sena.edu.co',
                'is_active'  => true,
                'rate_limit' => 2,
                'headers'    => [
                    'queries'   => [
                        'Ingeniero de Sistemas',
                        'Desarrollador',
                        'Programador',
                        'Analista desarrollador',
                        'Ingeniero de software',
                    ],
                    'blacklist' => ['bairesdev'],
                ],
            ],
            [
                'name'       => 'jobleads',
                'url'        => 'https://www.jobleads.com',
                'is_active'  => true,
                'rate_limit' => 2,
                'headers'    => [
                    'queries'   => [
                        'programador',
                        'desarrollador',
                        'software',
                        'backend',
                        'fullstack',
                        'php',
                        'laravel',
                    ],
                    'blacklist' => ['bairesdev'],
                ],
            ],
        ];

        foreach ($sources as $data) {
            Source::updateOrCreate(
                ['name' => $data['name']],
                $data
            );
        }
    }
}
