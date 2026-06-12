import 'package:centum/data/models/transaction.dart';
import 'package:centum/data/repositories/backup_repository.dart';

class BackupService {
  Future<String> createBackup() {
    return BackupRepository.createBackup();
  }

  Future<bool> restoreBackup(String path) {
    return BackupRepository.restoreBackup(path);
  }

  Future<List<BackupInfo>> listBackups() {
    return BackupRepository.listBackups();
  }

  Future<String> clearAllData() {
    return BackupRepository.clearAllData();
  }
}