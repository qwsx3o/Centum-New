import 'package:flutter/material.dart';
import 'package:centum/core/theme/app_theme.dart';
import 'package:centum/core/constants/dimensions.dart';
import 'package:centum/data/models/transaction.dart';
import 'package:collection/collection.dart';

class DayGroupWidget extends StatelessWidget {
  final DayGroup dayGroup;

  const DayGroupWidget({super.key, required this.dayGroup});

  @override
  Widget build(BuildContext context) {
    final netChange = dayGroup.income + dayGroup.capital - dayGroup.expenses;
    final netColor = netChange >= 0 ? AppColors.income : AppColors.expense;
    final netSign = netChange >= 0 ? '+' : '';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: Dimensions.md,
            vertical: Dimensions.sm,
          ),
          child: Row(
            children: [
              Text(
                dayGroup.date,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  color: AppColors.subtext,
                ),
              ),
              const Spacer(),
              Text(
                '$netSign${netChange.toStringAsFixed(0)}₽',
                style: TextStyle(
                  color: netColor,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
        ...dayGroup.transactions
            .mapIndexed((i, tx) => _buildTxCard(tx, i == dayGroup.transactions.length - 1)),
      ],
    );
  }

  Widget _buildTxCard(Transaction tx, bool isLast) {
    final isIncome = tx.type == 'income';
    final isCapital = tx.type == 'capital';

    Color iconColor;
    IconData icon;
    String sign;
    if (isCapital) {
      iconColor = AppColors.capital;
      icon = Icons.savings;
      sign = '+';
    } else if (isIncome) {
      iconColor = AppColors.income;
      icon = Icons.arrow_downward;
      sign = '+';
    } else {
      iconColor = AppColors.expense;
      icon = Icons.arrow_upward;
      sign = '-';
    }

    return Container(
      margin: EdgeInsets.only(
        left: Dimensions.md,
        right: Dimensions.md,
        bottom: isLast ? Dimensions.sm : 0,
      ),
      padding: const EdgeInsets.symmetric(
        horizontal: Dimensions.sm,
        vertical: Dimensions.sm,
      ),
      decoration: BoxDecoration(
        color: AppColors.card,
        border: Border(
          bottom: BorderSide(
            color: isLast ? Colors.transparent : AppColors.bg,
          ),
        ),
      ),
      child: Row(
        children: [
          Icon(icon, color: iconColor, size: 16),
          const SizedBox(width: Dimensions.sm),
          Expanded(
            child: Text(
              tx.categoryName,
              style: const TextStyle(color: AppColors.text),
            ),
          ),
          if (tx.note.isNotEmpty)
            Text(
              tx.note,
              style: const TextStyle(color: AppColors.subtext, fontSize: 11),
            ),
          const SizedBox(width: Dimensions.sm),
          Text(
            '$sign${tx.amount.toStringAsFixed(0)}₽',
            style: TextStyle(
              color: iconColor,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}