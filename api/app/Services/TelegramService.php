<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class TelegramService
{
    private string $token;
    private string $chatId;
    private const MAX_LENGTH = 4000;

    public function __construct()
    {
        $this->token  = config('services.telegram.token');
        $this->chatId = config('services.telegram.chat_id');
    }

    public function send(string $message): void
    {
        if (empty($this->token) || empty($this->chatId)) {
            Log::warning('TelegramService: token o chat_id no configurado.');
            return;
        }

        $chunks = $this->splitMessage($message);

        foreach ($chunks as $chunk) {
            $response = Http::post("https://api.telegram.org/bot{$this->token}/sendMessage", [
                'chat_id'    => $this->chatId,
                'text'       => $chunk,
                'parse_mode' => 'HTML',
            ]);

            if (!$response->successful()) {
                Log::error('TelegramService: error al enviar mensaje', [
                    'status' => $response->status(),
                    'body'   => $response->body(),
                ]);
            }
        }
    }

    private function splitMessage(string $message): array
    {
        if (mb_strlen($message) <= self::MAX_LENGTH) {
            return [$message];
        }

        $chunks = [];
        $lines  = explode("\n", $message);
        $current = '';

        foreach ($lines as $line) {
            $candidate = $current === '' ? $line : $current . "\n" . $line;

            if (mb_strlen($candidate) > self::MAX_LENGTH) {
                if ($current !== '') {
                    $chunks[] = $current;
                }
                $current = $line;
            } else {
                $current = $candidate;
            }
        }

        if ($current !== '') {
            $chunks[] = $current;
        }

        return $chunks;
    }
}