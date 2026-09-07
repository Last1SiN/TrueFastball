# TrueFastball

[English](README.md) | [Русский](README_RU.md)

TrueFastball делает Fastball в Borderlands 3 ближе по ощущению к версии из Borderlands 2: повышает урон и делает бросок отзывчивее, намеренно сохраняя штатную скорость полёта и траекторию Fastball из BL3.

Мод умножает уже рассчитанный runtime `GrenadeDamage`, сохраняя штатное масштабирование по уровню и Mayhem, и временно ускоряет протестированную анимацию броска только во время броска Fastball.

## Возможности

- Множитель урона применяется только к гранатам Fastball.
- **Fastball Damage Multiplier** по умолчанию: `2.56`.
- Умножает runtime `GrenadeDamage`, а не записывает абсолютное значение урона.
- Сохраняет штатное масштабирование по уровню и Mayhem.
- Обновляет значение Damage на карточке Fastball в соответствии с активным множителем.
- **Throw Animation RateScale** по умолчанию: `2.0`.
- После завершения конкретного grenade action восстанавливает временно изменённый RateScale анимации.
- Не изменяет скорость полёта Fastball, gravity, upward velocity или траекторию.
- Выводит обе настройки в Mod Menu.
- Проверяет вручную изменённые или некорректные сохранённые значения перед использованием.
- При обычной работе пишет в лог только ошибки.

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
4. Удалите старые Fastball test/probe-сборки, чтобы одновременно загружалась только одна runtime-версия мода для Fastball.
5. Запустите игру, откройте **MODS -> TrueFastball**, включите мод и при необходимости настройте оба параметра через **Options**.

Для обновления замените существующий `.sdkmod` новым файлом и перезапустите игру.

## Совместимость и лицензия

- Множитель урона применяется только к гранатам Fastball.
- Штатные скорость полёта, gravity и траектория Fastball из Borderlands 3 намеренно не изменяются.
- Кооператив: **Unknown** — сценарий, где мод установлен только у клиента, а у хоста его нет, пока не проверен.
- Лицензия: **GPL-3.0**

## Credits

**Development:** Sol / GPT-5.6 Sol  
**Design, testing & QA:** Last1SiN

**BL3 PythonSDK / Oak Mod Manager:** создан [apple1417](https://github.com/apple1417) при участии проекта и контрибьюторов [BL-SDK](https://github.com/bl-sdk).
