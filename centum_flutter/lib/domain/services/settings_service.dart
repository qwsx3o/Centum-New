import 'package:centum/data/repositories/settings_repository.dart';

class SettingsService {
  Map<String, dynamic> _settings = {};

  Future<Map<String, dynamic>> loadSettings() async {
    _settings = await SettingsRepository.load();
    return _settings;
  }

  Future<void> updateSettings(
    String key1,
    String key2,
    dynamic value,
  ) async {
    _settings = await SettingsRepository.load();
    if (_settings[key1] is Map<String, dynamic>) {
      final nested = Map<String, dynamic>.from(_settings[key1] as Map);
      nested[key2] = value;
      _settings[key1] = nested;
    }
    await SettingsRepository.save(_settings);
  }

  dynamic get(String key1, String key2) {
    final nested = _settings[key1];
    if (nested is Map<String, dynamic>) {
      return nested[key2];
    }
    return null;
  }

  Future<void> saveNow() async {
    await SettingsRepository.save(_settings);
  }
}