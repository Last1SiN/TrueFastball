# TrueFastball

**Мод PythonSDK / Oak для Borderlands 3**

Текущий релиз: **v1.0**

> Готовые к установке `.sdkmod` публикуются в разделе **Releases**.  
> Файлы в репозитории являются исходниками мода.

---

TrueFastball делает Fastball в Borderlands 3 ближе по ощущению к версии из Borderlands 2: повышает урон и ускоряет анимацию броска, но намеренно сохраняет штатную скорость полёта и траекторию Fastball из BL3.

Мод работает только с Fastball. Он умножает уже рассчитанный runtime `GrenadeDamage`, сохраняя штатное масштабирование по уровню и Mayhem, и временно ускоряет протестированную анимацию броска только во время броска Fastball.

## Возможности

- Изменяет урон только у фактического Fastball delivery.
- Значение **Fastball Damage Multiplier** по умолчанию: `2.56`.
- Умножает runtime `GrenadeDamage`, а не записывает абсолютное значение урона.
- Сохраняет штатное масштабирование урона по уровню и Mayhem.
- Значение **Throw Animation RateScale** по умолчанию: `2.0`.
- После завершения конкретного grenade action восстанавливает временно изменённый RateScale анимации.
- Не изменяет скорость полёта Fastball.
- Не изменяет gravity, upward velocity или траекторию снаряда.
- Выводит обе настройки релиза в Mod Menu.
- Проверяет вручную изменённые или некорректные сохранённые настройки перед использованием.
- При нормальной работе мод не засоряет игровой лог; записываются только ошибки.

## Настройка

Протестированные значения по умолчанию:

- **Fastball Damage Multiplier:** `2.56`
- **Throw Animation RateScale:** `2.0`

Допустимые диапазоны:

- **Fastball Damage Multiplier:** `1.00-4.00`, шаг `0.01`
- **Throw Animation RateScale:** `1.0-5.0`, шаг `0.1`

Настройки доступны через **MODS -> TrueFastball -> Options**.

Текущее ускорение throw-animation через RateScale использует протестированные animation assets **FL4K / Beastmaster**. Изменение урона Fastball от этих animation assets не зависит.

TrueFastball намеренно не меняет штатную скорость полёта и траекторию Fastball в Borderlands 3.

## Требования

- Borderlands 3.
- [BL3 PythonSDK / Oak Mod Manager v1.11+ — актуальный стабильный релиз](https://github.com/bl-sdk/oak-mod-manager/releases/latest).
- [Официальная инструкция по установке BL3 SDK](https://bl-sdk.github.io/oak-mod-db/).

Oak Mod Manager v1.11 уже включает Mods Base 1.12, BL3 Mod Menu 1.8, Console Mod Menu 1.6, Keybinds 2.6, pyunrealsdk 1.10.0, UI Utils 1.4 и unrealsdk 3.2.0. При использовании этой или более новой совместимой версии Oak отдельно скачивать эти компоненты обычно не нужно.

## Установка

1. **Полностью закройте Borderlands 3.**
2. Если BL3 PythonSDK / Oak ещё не установлен или его нужно обновить, откройте [актуальный стабильный релиз Oak Mod Manager](https://github.com/bl-sdk/oak-mod-manager/releases/latest).
3. В разделе **Assets** скачайте именно **`bl3-sdk.zip`**, а не архивы `Source code`.
4. Найдите корневую папку Borderlands 3. В Steam: **Библиотека -> ПКМ по Borderlands 3 -> Управление -> Просмотреть локальные файлы**.
5. Распакуйте содержимое `bl3-sdk.zip` прямо в корневую папку Borderlands 3, согласившись на объединение папок/файлов и замену файлов при запросе. Полная процедура, включая Proton/Linux, находится в [официальной инструкции BL3 SDK](https://bl-sdk.github.io/oak-mod-db/).
6. Один раз запустите Borderlands 3 и убедитесь, что в главном меню появился пункт **MODS**.
7. Скачайте актуальный релиз TrueFastball.
8. Полностью закройте игру и скопируйте `TrueFastball.sdkmod` **не распаковывая** в:

   `Borderlands 3\sdk_mods\`

9. Удалите старые Fastball probe/test-сборки, чтобы одновременно загружалась только одна runtime-версия мода для Fastball.
10. Запустите/перезапустите Borderlands 3, откройте **MODS -> TrueFastball**, включите мод и откройте **Options** для настройки двух параметров при необходимости.

Для обновления TrueFastball замените существующий `TrueFastball.sdkmod` новой версией и перезапустите игру.

## Совместимость и лицензия

- Fastball scope: изменение урона применяется только к фактическому Fastball projectile delivery.
- Projectile behavior: штатные скорость, gravity и траектория Fastball из BL3 намеренно не изменяются.
- Персонажи: изменение урона общее; текущее ускорение throw-animation использует протестированные assets **FL4K / Beastmaster**.
- Кооператив: **Unknown** — сценарий, где мод установлен у клиента, но отсутствует у хоста, пока не проверен.
- Лицензия: **GPL-3.0**

## Credits

- **Development:** Sol / GPT-5.6 Sol
- **Design, testing & QA:** Last1SiN
- **BL3 PythonSDK / Oak Mod Manager:** создан [apple1417](https://github.com/apple1417) при участии проекта и контрибьюторов [BL-SDK](https://github.com/bl-sdk).
