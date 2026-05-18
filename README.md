# Task Scheduler

Task Scheduler adalah contoh scheduler sederhana berbasis Python untuk menjalankan task sesuai waktu terjadwal, action yang didaftarkan, dan quota per user. Project ini memakai penyimpanan in-memory sehingga cocok untuk demo, latihan arsitektur, atau fondasi awal sebelum dihubungkan ke database/queue sungguhan.

## Fitur

- Menjalankan task berdasarkan waktu dalam format `HH:MM`.
- Mendukung action berbasis strategy pattern: `sync`, `backup`, dan `delete`.
- Membatasi jumlah task yang dapat dijalankan per user menggunakan quota.
- Reservation quota dibuat thread-safe dengan `Lock`.
- Memisahkan domain model, repository, quota store, executor, action registry, dan scheduler.
- Menyediakan test dasar untuk skenario task due dan quota exceeded.

## Struktur Project

```text
.
|-- actions.py              # Strategy untuk action task dan action registry
|-- app.py                  # Entry point demo dan wiring dependency
|-- executor.py             # Validasi action, quota, dan eksekusi task
|-- models.py               # Dataclass Task dan ActionResult
|-- quota.py                # In-memory quota store per user
|-- repositories.py         # In-memory task repository
|-- scheduler.py            # Scheduler utama untuk menjalankan due task
`-- tests/
    `-- test-scheduler.py   # Unit test scheduler dan quota
```

## Requirement

- Python 3.10 atau lebih baru direkomendasikan.
- Tidak ada dependency eksternal untuk menjalankan aplikasi.
- `pytest` diperlukan hanya untuk menjalankan test.

## Cara Menjalankan

Clone repository:

```bash
git clone https://github.com/marfindev/task-scheduler.git
cd task-scheduler
```

Jalankan demo scheduler:

```bash
python3 app.py
```

Secara default, `app.py` menjalankan simulasi untuk waktu `12:00`:

```python
scheduler.run_pending(current_time="12:00")
```

Untuk menjalankan berdasarkan jam sistem saat ini, panggil:

```python
scheduler.run_pending()
```

## Menjalankan Test

Install `pytest` jika belum tersedia:

```bash
python3 -m pip install pytest
```

Lalu jalankan:

```bash
python3 -m pytest -q
```

## Format Task

Task dibuat dari dictionary melalui `Task.from_dict()`.

```python
{
    "user": "alice",
    "time": "12:00",
    "action": "sync",
    "target": "/data/x",
    "params": {
        "priority": "high"
    }
}
```

Field wajib:

- `user`: nama user pemilik task.
- `time`: waktu eksekusi dalam format `HH:MM`.
- `action`: nama action yang sudah didaftarkan di `ActionRegistry`.
- `target`: target yang diproses oleh action.

Field opsional:

- `id`: ID task. Jika tidak diisi, akan dibuat otomatis dengan UUID.
- `params`: konfigurasi tambahan untuk action.

## Konfigurasi Quota

Quota user didefinisikan dalam bentuk dictionary:

```python
users_config = {
    "alice": {
        "quota": 3,
        "executed": 0,
    },
    "bob": {
        "quota": 5,
        "executed": 0,
    },
}
```

Saat task akan dijalankan, executor memanggil `try_reserve()`. Jika quota user sudah habis, task tidak dieksekusi. Jika action gagal, quota dikembalikan dengan `release()`.

## Menambah Action Baru

Buat class baru yang mengimplementasikan `ActionStrategy`:

```python
from actions import ActionStrategy
from models import ActionResult, Task


class CompressAction(ActionStrategy):
    def execute(self, task: Task) -> ActionResult:
        return ActionResult(
            success=True,
            message=f"Compress completed for {task.target}",
        )
```

Daftarkan action tersebut ke registry:

```python
action_registry.register("compress", CompressAction())
```

Setelah itu task dapat memakai `"action": "compress"`.

## Alur Eksekusi

1. `SimpleScheduler.run_pending()` mengambil waktu saat ini atau menerima `current_time` dari parameter.
2. `InMemoryTaskRepository.get_due_tasks()` mencari task yang `scheduled_time`-nya sama.
3. `TaskExecutor.execute()` memvalidasi action dan quota user.
4. Action yang sesuai dijalankan melalui `ActionRegistry`.
5. Scheduler mengembalikan jumlah task yang berhasil dieksekusi.

## Catatan Pengembangan

Implementasi saat ini masih in-memory. Untuk kebutuhan production, beberapa bagian yang bisa ditingkatkan:

- Ganti `InMemoryTaskRepository` dengan database seperti PostgreSQL/MySQL.
- Simpan quota di database transaction atau Redis atomic counter.
- Tambahkan status task seperti `pending`, `running`, `success`, dan `failed`.
- Tambahkan retry policy, dead-letter handling, dan observability.
- Jalankan scheduler secara periodik dengan cron, worker loop, atau service manager.
