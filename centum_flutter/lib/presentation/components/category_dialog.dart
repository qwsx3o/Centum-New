import 'package:flutter/material.dart';
import 'package:centum/core/theme/app_theme.dart';
import 'package:centum/core/constants/dimensions.dart';
import 'package:centum/data/repositories/category_repository.dart';

class CategoryDialog extends StatefulWidget {
  const CategoryDialog({super.key});

  @override
  State<CategoryDialog> createState() => _CategoryDialogState();
}

class _CategoryDialogState extends State<CategoryDialog> {
  final _nameController = TextEditingController();
  String _selectedType = 'expense';
  String? _selectedColor;

  final _colors = [
    '#4CAF50', '#EF5350', '#42A5F5', '#AB47BC',
    '#FF7043', '#26C6DA', '#FFEE58', '#66BB6A',
    '#EC407A', '#78909C',
  ];

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: AppColors.surface,
      title: const Text('Новая категория',
          style: TextStyle(color: AppColors.text)),
      content: SizedBox(
        width: double.maxFinite,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SegmentedButton<String>(
              segments: const [
                ButtonSegment(value: 'income', label: Text('Доход')),
                ButtonSegment(value: 'expense', label: Text('Расход')),
              ],
              selected: {_selectedType},
              onSelectionChanged: (v) =>
                  setState(() => _selectedType = v.first),
              style: ButtonStyle(
                backgroundColor: WidgetStateProperty.resolveWith((states) {
                  if (states.contains(WidgetState.selected)) {
                    return _selectedType == 'income'
                        ? AppColors.income.withOpacity(0.2)
                        : AppColors.expense.withOpacity(0.2);
                  }
                  return AppColors.card;
                }),
              ),
            ),
            const SizedBox(height: Dimensions.md),
            TextField(
              controller: _nameController,
              decoration: const InputDecoration(labelText: 'Название'),
            ),
            const SizedBox(height: Dimensions.md),
            const Text('Цвет', style: TextStyle(color: AppColors.subtext)),
            const SizedBox(height: Dimensions.sm),
            Wrap(
              spacing: Dimensions.sm,
              runSpacing: Dimensions.sm,
              children: _colors.map((c) {
                final color = Color(int.parse(c.replaceFirst('#', '0xFF')));
                final isSelected = _selectedColor == c;
                return GestureDetector(
                  onTap: () => setState(() => _selectedColor = c),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    width: 32,
                    height: 32,
                    decoration: BoxDecoration(
                      color: color,
                      borderRadius: BorderRadius.circular(8),
                      border: isSelected
                          ? Border.all(color: AppColors.text, width: 2)
                          : null,
                    ),
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Отмена',
              style: TextStyle(color: AppColors.subtext)),
        ),
        ElevatedButton(
          onPressed: _submit,
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.accent,
          ),
          child: const Text('Создать',
              style: TextStyle(color: AppColors.text)),
        ),
      ],
    );
  }

  Future<void> _submit() async {
    final name = _nameController.text.trim();
    if (name.length < 2) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Минимум 2 символа')),
      );
      return;
    }
    try {
      await CategoryRepository.createCategory(name, _selectedType, _selectedColor);
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка: $e')),
        );
      }
    }
  }
}