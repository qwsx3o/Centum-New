import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;
import 'package:sqflite/sqflite.dart';
import 'package:archive/archive.dart';
import 'package:centum/core/constants/app_constants.dart';
import 'package:centum/core/database/database_helper.dart';
import 'package:centum/data/models/transaction.dart';
import 'package:centum/data/repositories/settings_repository.dart';

class BackupRepository {
  static Future<String> _getBackupDirPath() async {
    final dir = await getApplicationDocumentsDirectory();
    final backupDir = Directory(p.join(dir.path, AppConstants.backupDirName));
    if (!await backupDir.exists()) {
      await backupDir.create(recursive: true);
    }
    return backupDir.path;
  }

  static Future<String> createBackup() async {
    final backupDir = await _getBackupDirPath();
    final timestamp = DateTime.now().toIso8601String()
        .replaceAll(RegExp(r'[^0-9]'), '')
        .substring(0, 14);
    final timestampFormatted =
        '${timestamp.substring(0, 8)}_${timestamp.substring(8)}';
    final zipPath = p.join(
      backupDir,
      '${AppConstants.backupPrefix}$timestampFormatted.zip',
    );

    final dbPath = p.join(await getDatabasesPath(), AppConstants.dbName);
    final dbBytes = await File(dbPath).readAsBytes();

    final docsDir = await getApplicationDocumentsDirectory();
    final settingsFile = File(
      p.join(docsDir.path, AppConstants.settingsFileName),
    );
    final settingsBytes = await settingsFile.readAsBytes();

    final archive = Archive();
    archive.addFile(ArchiveFile('centum.db', dbBytes.length, dbBytes));
    archive.addFile(
      ArchiveFile('settings.json', settingsBytes.length, settingsBytes),
    );

    final data = ZipEncoder().encode(archive);
    await File(zipPath).writeAsBytes(data);

    return zipPath;
  }

  static Future<bool> restoreBackup(String archivePath) async {
    try {
      final bytes = await File(archivePath).readAsBytes();
      final archive = ZipDecoder().decodeBytes(bytes);

      final dbPath = p.join(await getDatabasesPath(), AppConstants.dbName);
      final docsDir = await getApplicationDocumentsDirectory();
      final settingsPath = p.join(
        docsDir.path,
        AppConstants.settingsFileName,
      );

      await DatabaseHelper.close();

      for (final file in archive) {
        if (file.name == 'centum.db') {
          await File(dbPath).writeAsBytes(file.content as List<int>);
        } else if (file.name == 'settings.json') {
          await File(settingsPath).writeAsBytes(file.content as List<int>);
        }
      }

      return true;
    } catch (_) {
      return false;
    }
  }

  static Future<List<BackupInfo>> listBackups() async {
    final backupDir = await _getBackupDirPath();
    final dir = Directory(backupDir);
    if (!await dir.exists()) return [];

    final files = await dir
        .list()
        .where((entity) =>
            entity is File &&
            entity.path.endsWith('.zip') &&
            p.basename(entity.path).startsWith(AppConstants.backupPrefix))
        .toList();

    files.sort((a, b) => b.path.compareTo(a.path));

    return files.map((file) {
      final stat = file.statSync();
      final modified = stat.modified;
      final sizeKb = (stat.size / 1024).round();
      return BackupInfo(
        name: p.basename(file.path),
        sizeKb: sizeKb,
        created: '${modified.year}-'
            '${modified.month.toString().padLeft(2, '0')}-'
            '${modified.day.toString().padLeft(2, '0')} '
            '${modified.hour.toString().padLeft(2, '0')}:'
            '${modified.minute.toString().padLeft(2, '0')}',
      );
    }).toList();
  }

  static Future<String> clearAllData() async {
    final backupPath = await createBackup();

    final db = await DatabaseHelper.instance;
    await db.delete('transactions');
    await db.delete(
      'categories',
      where: 'is_system = 0',
    );

    await SettingsRepository.save({
      'profile': {'family_members': 1},
      'app': {'currency': '₽', 'dark_mode': true},
    });

    return backupPath;
  }
}