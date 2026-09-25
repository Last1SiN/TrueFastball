# TrueFastball

[English](README.md) | [Русский](README_RU.md)

TrueFastball возвращает Fastball ощущение действительно мощной гранаты.

Мод повышает урон и ускоряет бросок, но не трогает штатную скорость полёта и траекторию из Borderlands 3. В итоге Fastball бьёт заметно сильнее и бросается быстрее, не превращаясь при этом в другую гранату.

Урон и скорость броска можно настроить через Mod Menu.

## Возможности

- Увеличивает урон Fastball; множитель по умолчанию — **2.56x**.
- Ускоряет анимацию броска; значение по умолчанию — **2.0x**.
- Не меняет штатную скорость полёта и траекторию Fastball.
- Урон продолжает нормально масштабироваться с уровнем и Mayhem.
- Значение Damage на карточке отражает активный множитель.
- Обе настройки доступны в Mod Menu.
- После броска возвращает временно изменённую скорость анимации.

## Настройка

Значения по умолчанию:

- **Fastball Damage Multiplier:** `2.56`
- **Throw Animation RateScale:** `2.0`

Допустимые диапазоны:

- **Fastball Damage Multiplier:** `1.00-4.00`, шаг `0.01`
- **Throw Animation RateScale:** `1.0-5.0`, шаг `0.1`

Настройки доступны через **MODS -> TrueFastball -> Options**.

Текущее ускорение throw-animation использует протестированные animation assets **FL4K / Beastmaster**. Изменение урона от этих animation assets не зависит.

## Требования

- Borderlands 3
- [BL3 PythonSDK / Oak Mod Manager](https://github.com/bl-sdk/oak-mod-manager/releases/latest)

Для установки и обновления SDK используйте [официальную инструкцию BL3 SDK / Oak](https://bl-sdk.github.io/oak-mod-db/).

## Установка мода

1. Установите или обновите BL3 PythonSDK / Oak по официальной инструкции выше.
2. Скачайте `TrueFastball.sdkmod` из [GitHub Releases](https://github.com/Last1SiN/TrueFastball/releases/latest).
3. При полностью закрытой Borderlands 3 скопируйте `.sdkmod` целиком в `Borderlands 3\sdk_mods\`. Сам `.sdkmod` распаковывать не нужно.
4. Запустите игру, откройте **MODS -> TrueFastball**, включите мод и при необходимости настройте оба параметра через **Options**.

Для обновления замените существующий `.sdkmod` новым файлом и перезапустите игру.

## Совместимость и лицензия

- Множитель урона применяется только к гранатам Fastball.
- Штатные скорость полёта, gravity и траектория Fastball из Borderlands 3 намеренно не изменяются.
- Кооператив: **Unknown** — сценарий, где мод установлен только у клиента, а у хоста его нет, пока не проверен.
- Лицензия: **GNU GPLv3 с [дополнительными условиями происхождения по Section 7](ADDITIONAL_TERMS.md)**

## Credits

**Development:** Sol / GPT-5.6 Sol  
**Design, testing & QA:** Last1SiN

**BL3 PythonSDK / Oak Mod Manager:** создан [apple1417](https://github.com/apple1417) при участии проекта и контрибьюторов [BL-SDK](https://github.com/bl-sdk).
