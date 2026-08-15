# factorygames-tezgah

FactoryGames hattının **0B pilot oyunu — "Tezgâh"**: izometrik mahalle pazarı tezgâhı;
sezon stoğu oyun başında bir kez verilir ve asla yenilenmez, her 30 saniyelik tur bir
gündür ve asıl karar tahsistir (neyi rafa koyacağın, kimi geri çevireceğin). Konsept kartı
ve seçim kaydı: FactoryGames
[`docs/factory/kavram/2026-08/secim.md`](https://github.com/serkankaval52-collab/FactoryGames/blob/arena/019fcd97-factorygames/docs/factory/kavram/2026-08/secim.md)
(KART A); stil paketi `duz-geometrik` / NET-SOKAK yönü
[`docs/standards/sanat-yonu/duz-geometrik.md`](https://github.com/serkankaval52-collab/FactoryGames/blob/arena/019fcd97-factorygames/docs/standards/sanat-yonu/duz-geometrik.md)
— palet hex'leri ve G5 üçlüsü oradan birebir alıntıdır. Aşama 2 plan belgesi:
[`docs/plan.md`](docs/plan.md). Norm kaynağı:
[FactoryGames/docs/PIPELINE.md](https://github.com/serkankaval52-collab/FactoryGames/blob/arena/019fcd97-factorygames/docs/PIPELINE.md)
· Repo kuralları: [CLAUDE.md](CLAUDE.md).

## Yerel koşum

```
python tools/lint/lint.py --kok .
python tools/lint/lint_varlik.py --kok .
python tools/events_parity.py --kok .
dotnet test tests/Core.Tests/Core.Tests.csproj -c Release
```

Unity gerektiren kanıtlar (EditMode/PlayMode, APK, xcodeproj) yerelde batchmode ile
üretilir — CI runner'ında Unity **yoktur** (C+ makine ilkesi);
`Assets/Editor/BuildScript.cs` içindeki menü komutları kullanılır.
