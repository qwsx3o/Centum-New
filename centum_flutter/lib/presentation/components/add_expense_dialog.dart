import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:centum/presentation/bloc/finance/finance_cubit.dart';
import 'package:centum/presentation/bloc/finance/finance_state.dart';
import 'package:centum/core/theme/app_theme.dart';
import 'package:centum/core/constants/app_constants.dart';
import 'package:centum/core/constants/dimensions.dart';
import 'package:centum/data/models/category.dart';
import 'package:centum/data/repositories/category_repository.dart';

class AddExpenseDialog extends StatefulWidget {
  const AddExpenseDialog({super.key});

  @override
  State<AddExpenseDialog> createState() => _AddExpenseDialogState();
}

class _AddExpenseDialogState extends State<AddExpenseDialog>
    with SingleTickerProviderStateMixin {
  final _amountController = TextEditingController();
  final _noteController = TextEditingController();
  List<Category> _categories = [];
  Category? _selectedCategory;
  bool _isLoading = true;
  bool _isPaused = false;
  int _countdown = AppConstants.pauseDurationSeconds;
  bool _showChoice = false;
  late AnimationController _animController;
  late Animation<double> _pulseAnim;
  String _titleText = 'Добавить расход';
  Color _titleColor = AppColors.expense;
  Color _bgColor = AppColors.surface;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
    _pulseAnim = Tween<double>(begin: 1.0, end: 1.05).animate(
      CurvedAnimation(parent: _animController, curve: Curves.easeInOut),
    );
    _loadCategories();
  }

  Future<void> _loadCategories() async {
    final cats = await CategoryRepository.getCategoriesByType('expense');
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
    _animController.dispose();
    super.dispose();
  }

  String _classify(String categoryName) {
    final name = categoryName.toLowerCase();
    final transmutation = [
      'образование', 'здоровье', 'навык', 'развитие',
      'обучение', 'курс',
    ];
    final pause = [
      'развлечен', 'спонтан', 'желани', 'удовольстви',
      'хобби', 'игр', 'ресторан', 'кафе',
    ];
    for (final kw in transmutation) {
      if (name.contains(kw)) return 'transmutation';
    }
    for (final kw in pause) {
      if (name.contains(kw)) return 'pause';
    }
    return 'normal';
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: _bgColor,
      title: AnimatedDefaultTextStyle(
        duration: const Duration(milliseconds: 300),
        style: TextStyle(
          fontSize: Dimensions.textXl,
          fontWeight: FontWeight.bold,
          color: _titleColor,
        ),
        child: Text(_titleText),
      ),
      content: SingleChildScrollView(
        child: SizedBox(
          width: double.maxFinite,
          child: _isLoading
              ? const Center(child: CircularProgressIndicator())
              : Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    BlocBuilder<FinanceCubit, FinanceState>(
                      builder: (context, state) {
                        return Container(
                          padding: const EdgeInsets.all(Dimensions.sm),
                          decoration: BoxDecoration(
                            color: AppColors.available.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(Dimensions.radiusSm),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.account_balance_wallet,
                                  color: AppColors.available, size: 20),
                              const SizedBox(width: Dimensions.sm),
                              Text(
                                'Доступно: ${state.summary.available.toStringAsFixed(0)}₽',
                                style: const TextStyle(color: AppColors.available),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: Dimensions.md),
                    TextField(
                      controller: _amountController,
                      keyboardType: TextInputType.number,
                      enabled: !_isPaused,
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
                                            : AppColors.expense,
                                        borderRadius: BorderRadius.circular(2),
                                      ),
                                    ),
                                    const SizedBox(width: Dimensions.sm),
                                    Text(c.name),
                                  ],
                                ),
                              ))
                          .toList(),
                      onChanged: _isPaused ? null : (c) =>
                          setState(() => _selectedCategory = c),
                    ),
                    const SizedBox(height: Dimensions.md),
                    TextField(
                      controller: _noteController,
                      decoration: const InputDecoration(labelText: 'Заметка'),
                      enabled: !_isPaused,
                      maxLines: 2,
                    ),
                    if (_isPaused) ...[
                      const SizedBox(height: Dimensions.md),
                      AnimatedBuilder(
                        animation: _pulseAnim,
                        builder: (context, child) => Transform.scale(
                          scale: _pulseAnim.value,
                          child: child,
                        ),
                        child: Column(
                          children: [
                            const SizedBox(
                              width: 40,
                              height: 40,
                              child: CircularProgressIndicator(
                                color: AppColors.accent,
                                strokeWidth: 3,
                              ),
                            ),
                            const SizedBox(height: Dimensions.sm),
                            Text(
                              '$_countdown',
                              style: const TextStyle(
                                fontSize: Dimensions.textXxl,
                                fontWeight: FontWeight.bold,
                                color: AppColors.accent,
                              ),
                            ),
                            const SizedBox(height: Dimensions.sm),
                            Text(
                              'Истинное богатство — это способность '
                              'контролировать желания. Эти ${_amountController.text}₽ '
                              'станут ${(double.tryParse(_amountController.text) ?? 0) * AppConstants.futureValueMultiplier}₽ '
                              'через 10 лет. Твоё решение, Правитель.',
                              style: const TextStyle(
                                color: AppColors.subtext,
                                fontSize: Dimensions.textSm,
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      ),
                      if (_showChoice) ...[
                        const SizedBox(height: Dimensions.md),
                        Row(
                          children: [
                            Expanded(
                              child: TextButton(
                                onPressed: _commit,
                                child: const Text(
                                  'Осознаю. Трачу.',
                                  style: TextStyle(color: AppColors.subtext),
                                ),
                              ),
                            ),
                            const SizedBox(width: Dimensions.sm),
                            Expanded(
                              child: ElevatedButton.icon(
                                onPressed: _keepInCapital,
                                icon: const Icon(Icons.shield, size: 18),
                                label: const Text('В Капитал'),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: AppColors.accent,
                                  foregroundColor: AppColors.text,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ],
                  ],
                ),
        ),
      ),
      actions: _isPaused
          ? []
          : [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Отмена',
                    style: TextStyle(color: AppColors.subtext)),
              ),
              ElevatedButton(
                onPressed: _onSubmit,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.expense,
                ),
                child: const Text('Добавить',
                    style: TextStyle(color: AppColors.text)),
              ),
            ],
    );
  }

  Future<void> _onSubmit() async {
    final amount = double.tryParse(_amountController.text);
    if (amount == null || amount <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Введите корректную сумму')),
      );
      return;
    }
    if (_selectedCategory == null) return;

    final mechanic = _classify(_selectedCategory!.name);

    if (mechanic == 'transmutation') {
      try {
        await context
            .read<FinanceCubit>()
            .addExpense(amount, _selectedCategory!.id, note: _noteController.text);
        if (!mounted) return;
        setState(() {
          _titleColor = AppColors.expense;
          _bgColor = AppColors.warmBg;
        });
        await Future.delayed(const Duration(milliseconds: 100));
        if (!mounted) return;
        setState(() {
          _titleText = 'Трансмутация';
          _titleColor = AppColors.accent;
          _bgColor = AppColors.warmBg;
        });
        await Future.delayed(const Duration(milliseconds: 900));
        if (!mounted) return;
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Ты не потратил эти монеты. Ты конвертировал их '
              'в самый дорогой актив — себя. Ни одно правительство '
              'не может обложить налогом знания.',
            ),
          ),
        );
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Ошибка: $e')),
          );
        }
      }
      return;
    }

    if (mechanic == 'pause') {
      setState(() => _isPaused = true);
      _animController.repeat(reverse: true);
      _startCountdown();
      return;
    }

    await _commit();
  }

  void _startCountdown() {
    Future.doWhile(() async {
      await Future.delayed(const Duration(seconds: 1));
      if (!mounted) return false;
      setState(() {
        _countdown--;
        if (_countdown <= 0) {
          _showChoice = true;
          _animController.stop();
          _animController.reset();
        }
      });
      return _countdown > 0 && mounted;
    });
  }

  Future<void> _commit() async {
    final amount = double.tryParse(_amountController.text);
    if (amount == null || amount <= 0 || _selectedCategory == null) return;

    try {
      await context
          .read<FinanceCubit>()
          .addExpense(amount, _selectedCategory!.id, note: _noteController.text);
      if (mounted) Navigator.pop(context);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка: $e')),
        );
      }
    }
  }

  Future<void> _keepInCapital() async {
    setState(() {
      _titleText = 'Воля Патриции';
      _titleColor = AppColors.accent;
      _bgColor = AppColors.warmBg;
    });
    for (int i = 0; i < 3; i++) {
      await Future.delayed(const Duration(milliseconds: 150));
      if (!mounted) return;
      setState(() => _bgColor = AppColors.accent.withOpacity(0.3));
      await Future.delayed(const Duration(milliseconds: 150));
      if (!mounted) return;
      setState(() => _bgColor = AppColors.warmBg);
    }
    await Future.delayed(const Duration(milliseconds: 500));
    if (!mounted) return;
    Navigator.pop(context);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Аркад гордится твоей волей! Капитал сохранён.'),
      ),
    );
  }
}