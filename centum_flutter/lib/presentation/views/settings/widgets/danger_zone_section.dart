import 'package:flutter/material.dart';
import 'package:centum/core/theme/app_theme.dart';
import 'package:centum/core/constants/dimensions.dart';
import 'package:centum/domain/services/backup_service.dart';

class DangerZoneSection extends StatefulWidget {
  const DangerZoneSection({super.key});

  @override
  State<DangerZoneSection> createState() => _DangerZoneSectionState();
}

class _DangerZoneSectionState extends State<DangerZoneSection> {
  final _service = BackupService();
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.card,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(Dimensions.radiusSm),
        side: const BorderSide(color: AppColors.expense, width: 1),
      ),
      child: Padding(
        padding: const EdgeInsets.all(Dimensions.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.warning_amber, color: AppColors.expense, size: 20),
                const SizedBox(width: Dimensions.sm),
                const Text('Опасная зона',
                    style: TextStyle(
                      fontSize: Dimensions.textLg,
                      fontWeight: FontWeight.bold,
                      color: AppColors.expense,
                    )),
              ],
            ),
            const SizedBox(height: Dimensions.md),
            const Text(
              'Это удалит все данные. Сначала будет создан автоматический бэкап.',
              style: TextStyle(color: AppColors.subtext, fontSize: 12),
            ),
            const SizedBox(height: Dimensions.md),
            ElevatedButton.icon(
              onPressed: _isLoading ? null : _confirmClear,
              icon: _isLoading
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.delete_forever, size: 18),
              label: const Text('Очистить все данные'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.expense.withOpacity(0.2),
                foregroundColor: AppColors.expense,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _confirmClear() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.surface,
        title: const Text('Очистить все данные?',
            style: TextStyle(color: AppColors.expense)),
        content: const Text(
          'Будет создан автоматический бэкап перед очисткой. '
          'Это действие нельзя отменить.',
          style: TextStyle(color: AppColors.subtext),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Отмена',
                style: TextStyle(color: AppColors.subtext)),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              _clearData();
            },
            child: const Text('Очистить',
                style: TextStyle(color: AppColors.expense)),
          ),
        ],
      ),
    );
  }

  Future<void> _clearData() async {
    setState(() => _isLoading = true);
    try {
      final backupPath = await _service.clearAllData();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Данные очищены. Бэкап: $backupPath')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }
}