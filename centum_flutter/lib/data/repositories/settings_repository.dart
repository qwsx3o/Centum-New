import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;
import '../../core/constants/app_constants.dart';

class SettingsRepository {
  static const Map<String, dynamic> _defaults = {
    'profile': {'family_members': 1},
    'app': {'currency': '₽', 'dark_mode': true},
  };

  static Future<Map<String, dynamic>> load() async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      final file = File(p.join(dir.path, AppConstants.settingsFileName));
      if (!await file.exists()) {
        return Map<String, dynamic>.from(_defaults);
      }
      final contents = await file.readAsString();
      final data = json.decode(contents) as Map<String, dynamic>;
      return _mergeWithDefaults(data);
    } catch (_) {
      return Map<String, dynamic>.from(_defaults);
    }
  }

  static Future<void> save(Map<String, dynamic> settings) async {
    final dir = await getApplicationDocumentsDirectory();
    final file = File(p.join(dir.path, AppConstants.settingsFileName));
    await file.writeAsString(json.encode(settings));
  }

  static Map<String, dynamic> _mergeWithDefaults(Map<String, dynamic> data) {
    final merged = Map<String, dynamic>.from(_defaults);
    for (final key in data.keys) {
      if (merged[key] is Map && data[key] is Map) {
        merged[key] = {
          ...Map<String, dynamic>.from(merged[key] as Map),
          ...Map<String, dynamic>.from(data[key] as Map),
        };
      } else {
        merged[key] = data[key];
      }
    }
    return merged;
  }
}