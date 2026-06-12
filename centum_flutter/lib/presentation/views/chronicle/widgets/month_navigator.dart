import 'package:flutter/material.dart';
import 'package:centum/core/theme/app_theme.dart';
import 'package:centum/core/constants/dimensions.dart';

class MonthNavigator extends StatelessWidget {
  final int year;
  final int month;
  final VoidCallback onPrevious;
  final VoidCallback onNext;
  final bool canGoForward;

  const MonthNavigator({
    super.key,
    required this.year,
    required this.month,
    required this.onPrevious,
    required this.onNext,
    required this.canGoForward,
  });

  static const _months = [
    '', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',
  ];

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        IconButton(
          onPressed: onPrevious,
          icon: const Icon(Icons.chevron_left, color: AppColors.text),
        ),
        Text(
          '${_months[month]} $year',
          style: const TextStyle(
            fontSize: Dimensions.textXl,
            fontWeight: FontWeight.bold,
            color: AppColors.text,
          ),
        ),
        IconButton(
          onPressed: canGoForward ? onNext : null,
          icon: Icon(Icons.chevron_right,
              color: canGoForward ? AppColors.text : AppColors.muted),
        ),
      ],
    );
  }
}