import 'package:flutter/material.dart';
import 'package:centum/core/theme/app_theme.dart';
import 'package:centum/core/constants/dimensions.dart';
import 'package:centum/data/models/category.dart';
import 'package:centum/data/repositories/category_repository.dart';
import 'package:centum/presentation/components/category_dialog.dart';

class CategoriesSection extends StatefulWidget {
  const CategoriesSection({super.key});

  @override
  State<CategoriesSection> createState() => _CategoriesSectionState();
}

class _CategoriesSectionState extends State<CategoriesSection> {
  List<Category> _incomeCategories = [];
  List<Category> _expenseCategories = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final income = await CategoryRepository.getCategoriesByType('income');
    final expense = await CategoryRepository.getCategoriesByType('expense');
    setState(() {
      _incomeCategories = income;
      _expenseCategories = expense;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.card,
      child: Padding(
        padding: const EdgeInsets.all(Dimensions.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Категории',
                style: TextStyle(
                  fontSize: Dimensions.textLg,
                  fontWeight: FontWeight.bold,
                  color: AppColors.text,
                )),
            const SizedBox(height: Dimensions.md),
            _sectionHeader('Доходы', AppColors.income),
            ..._incomeCategories.map((c) => _categoryTile(c)),
            const SizedBox(height: Dimensions.md),
            _sectionHeader('Расходы', AppColors.expense),
            ..._expenseCategories.map((c) => _categoryTile(c)),
            const SizedBox(height: Dimensions.md),
            ElevatedButton.icon(
              onPressed: _addCategory,
              icon: const Icon(Icons.add, size: 18),
              label: const Text('Добавить'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.accent,
                foregroundColor: AppColors.text,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _sectionHeader(String title, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: Dimensions.xs),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(width: Dimensions.sm),
          Text(title,
              style: TextStyle(
                color: color,
                fontWeight: FontWeight.w500,
                fontSize: Dimensions.textSm,
              )),
        ],
      ),
    );
  }

  Widget _categoryTile(Category cat) {
    final color = cat.color != null
        ? Color(int.parse(cat.color!.replaceFirst('#', '0xFF')))
        : AppColors.subtext;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Container(
            width: 10,
            height: 10,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(width: Dimensions.sm),
          Expanded(
            child: Text(
              cat.name,
              style: TextStyle(
                color: cat.isSystem ? AppColors.subtext : AppColors.text,
                fontStyle: cat.isSystem ? FontStyle.italic : FontStyle.normal,
              ),
            ),
          ),
          if (!cat.isSystem)
            GestureDetector(
              onTap: () => _deleteCategory(cat),
              child: const Icon(Icons.delete_outline,
                  color: AppColors.expense, size: 18),
            ),
        ],
      ),
    );
  }

  Future<void> _addCategory() async {
    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => const CategoryDialog(),
    );
    if (result == true) _load();
  }

  Future<void> _deleteCategory(Category cat) async {
    final ok = await CategoryRepository.deleteCategory(cat.id);
    if (ok) {
      _load();
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Нельзя удалить системную категорию')),
        );
      }
    }
  }
}