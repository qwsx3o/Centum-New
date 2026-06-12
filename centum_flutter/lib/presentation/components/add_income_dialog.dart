import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:centum/presentation/bloc/finance/finance_cubit.dart';
import 'package:centum/core/theme/app_theme.dart';
import 'package:centum/core/constants/dimensions.dart';
import 'package:centum/data/models/category.dart';
import 'package:centum/data/repositories/category_repository.dart';

class AddIncomeDialog extends StatefulWidget {
  const AddIncomeDialog({super.key});

  @override
  State<AddIncomeDialog> createState() => _AddIncomeDialogState();
}

class _AddIncomeDialogState extends State<AddIncomeDialog> {
  final _amountController = TextEditingController();
  final _noteController = TextEditingController();
  List<Category> _categories = [];
  Category? _selectedCategory;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadCategories();
  }

  Future<void> _loadCategories() async {
    final cats = await CategoryRepository.getCategoriesByType('income');
    setState(() {
      _categories = cats;
      if (cats.isNotEmpty) _selectedCategory = cats.first;
      _isLoading = false;
    });
  }

  @override
  void dispose() {
    _amountController.dispose();
    _noteController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: AppColors.surface,
      title: const Text('Добавить доход',
          style: TextStyle(color: AppColors.text)),
      content: SingleChildScrollView(
        child: SizedBox(
          width: double.maxFinite,
          child: _isLoading
              ? const Center(child: CircularProgressIndicator())
              : Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(Dimensions.sm),
                      decoration: BoxDecoration(
                        color: AppColors.accent.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(Dimensions.radiusSm),
                        border: Border.all(
                            color: AppColors.accent.withOpacity(0.3)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.info_outline,
                              color: AppColors.accent, size: 20),
                          const SizedBox(width: Dimensions.sm),
                          Expanded(
                            child: Text(
                              '10% автоматически уходит в Капитал',
                              style: TextStyle(
                                fontSize: Dimensions.textSm,
                                color: AppColors.accent,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: Dimensions.md),
                    TextField(
                      controller: _amountController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Сумма',
                        prefixText: '₽ ',
                      ),
                    ),
                    const SizedBox(height: Dimensions.md),
                    DropdownButtonFormField<Category>(
                      value: _selectedCategory,
                      decoration: const InputDecoration(labelText: 'Категория'),
                      dropdownColor: AppColors.card,
                      items: _categories
                          .map((c) => DropdownMenuItem(
                                value: c,
                                child: Row(
                                  children: [
                                    Container(
                                      width: 12,
                                      height: 12,
                                      decoration: BoxDecoration(
                                        color: c.color != null
                                            ? Color(int.parse(
                                                c.color!.replaceFirst('#', '0xFF')))
                                            : AppColors.income,
                                        borderRadius: BorderRadius.circular(2),
                                      ),
                                    ),
                                    const SizedBox(width: Dimensions.sm),
                                    Text(c.name),
                                  ],
                                ),
                              ))
                          .toList(),
                      onChanged: (c) =>
                          setState(() => _selectedCategory = c),
                    ),
                    const SizedBox(height: Dimensions.md),
                    TextField(
                      controller: _noteController,
                      decoration: const InputDecoration(labelText: 'Заметка'),
                      maxLines: 2,
                    ),
                  ],
                ),
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
            backgroundColor: AppColors.income,
          ),
          child: const Text('Добавить',
              style: TextStyle(color: AppColors.text)),
        ),
      ],
    );
  }

  Future<void> _submit() async {
    final amount = double.tryParse(_amountController.text);
    if (amount == null || amount <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Введите корректную сумму')),
      );
      return;
    }
    if (_selectedCategory == null) return;

    try {
      await context
          .read<FinanceCubit>()
          .addIncome(amount, _selectedCategory!.id, note: _noteController.text);
      if (mounted) Navigator.pop(context);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка: $e')),
        );
      }
    }
  }
}