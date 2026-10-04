# 06 — Trace list (21 traces)

> **Nguồn:** Langfuse Public API `GET /api/public/v2/observations`, project cá nhân `day13-k4-l3a-2A202602372` (region `us.cloud.langfuse.com`, project id `cmumbflhq10gqad0cv6m5j8us`).
> **Loại evidence:** export text. Theo `docs/SUBMISSION.md`, mục này vẫn cần ảnh chụp Langfuse UI.

Đây là các root trace do chính workload của học viên tạo ra (load test, PII test, prompt test, challenge).

| # | start (UTC) | trace_id | correlation_id | feature | latency (s) |
|---:|---|---|---|---|---:|
| 1 | 2026-09-29T09:04:13.835Z | `943ced24a1fb6cb7313965eaf8d1721c` | `req-b1c83a89` | summary | 2.134 |
| 2 | 2026-09-29T09:04:19.300Z | `85b610af65f3b8554cb3ed6b820f6918` | `req-0a83fe57` | qa | 0.152 |
| 3 | 2026-09-29T09:04:19.460Z | `5321f494f9f205cb2c295dcb10639b72` | `req-653c4cd1` | qa | 0.158 |
| 4 | 2026-09-29T09:04:19.634Z | `fe2811c31d8af472a591e3b639415c31` | `req-5330ed2f` | qa | 0.151 |
| 5 | 2026-09-29T09:04:19.794Z | `4b1a539a9dd434e3817e5849b9e94342` | `req-6b7f6261` | qa | 0.156 |
| 6 | 2026-09-29T09:04:19.967Z | `a87f4210df057a5d0cef8c0a8ba0bd55` | `req-60359ef9` | summary | 0.155 |
| 7 | 2026-09-29T09:04:20.134Z | `bd1c8702b471a4dc6a6bbbfbac7f05a8` | `req-db59f77a` | qa | 0.154 |
| 8 | 2026-09-29T09:04:20.305Z | `1584fd294883457c0a8269085f1ce85a` | `req-6de08ef2` | qa | 0.152 |
| 9 | 2026-09-29T09:04:20.468Z | `db90250b479b424d989755f30734754d` | `req-6c1eb315` | qa | 0.154 |
| 10 | 2026-09-29T09:04:20.634Z | `e02d58fdefa660367af03f9acb8f1dc7` | `req-696af745` | qa | 0.156 |
| 11 | 2026-09-29T09:04:20.860Z | `8268beb99cccd321588b7cffab86a923` | `req-a1b2c3d4` | qa | 0.154 |
| 12 | 2026-09-29T09:05:56.767Z | `97ec27143efb9cb792fe2826e555be87` | `req-cad10002` | qa | 1.089 |
| 13 | 2026-09-29T09:06:53.542Z | `8facc588cefac3ad43652262f3d76b1d` | `req-0b1c0004` | qa | 1.161 |
| 14 | 2026-09-29T09:08:38.766Z | `2c423dcf781b71e37c369d31cb56f59c` | `req-ba5e0011` | qa | 1.056 |
| 15 | 2026-09-29T09:09:00.401Z | `5f1f9a56f748c303b971340b1a684a9f` | `req-0f0d0013` | qa | 1.061 |
| 16 | 2026-09-29T09:09:25.801Z | `78f725bba5d5c77b003926aa2c333e6e` | `req-0b1c0014` | qa | 1.866 |
| 17 | 2026-09-29T09:10:25.344Z | `fe47bc4c4863d5f87bd5475bb657f61e` | `req-a214b648` | monitoring | 3.625 |
| 18 | 2026-09-29T09:10:28.982Z | `79c6cd4c01057f828cbdacf8bb137043` | `req-d6fcfb37` | monitoring | 2.677 |
| 19 | 2026-09-29T09:10:31.678Z | `de9cc0bba73b29ffa1616e735093ee5c` | `req-4c7596ed` | monitoring | 2.653 |
| 20 | 2026-09-29T09:10:34.343Z | `11afa744533f7867d6bdb2e8e335c97a` | `req-8064368c` | monitoring | 2.658 |
| 21 | 2026-09-29T09:10:37.014Z | `6aea9a79639df4f7a7297dcd27aa4887` | `req-3a633748` | monitoring | 2.653 |

Các dòng 17–21 là trace của challenge CP3; dòng 17 là request bất thường (`req-a214b648`).
