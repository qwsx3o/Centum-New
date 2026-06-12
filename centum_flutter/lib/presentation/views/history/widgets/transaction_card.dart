import 'package:flutter/material.dart';
import 'package:centum/core/theme/app_theme.dart';
import 'package:centum/core/constants/dimensions.dart';
import 'package:centum/data/models/transaction.dart';

class TransactionCard extends StatelessWidget {
  final Transaction transaction;
  final VoidCallback onDelete;

  const TransactionCard({
    super.key,
    required this.transaction,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final isIncome = transaction.type == 'income';
    final isCapital = transaction.type == 'capital';

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

    return Card(
      color: AppColors.card,
      margin: const EdgeInsets.only(bottom: Dimensions.sm),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: iconColor.withOpacity(0.1),
          child: Icon(icon, color: iconColor, size: 20),
        ),
        title: Text(
          transaction.categoryName,
          style: const TextStyle(
            color: AppColors.text,
            fontWeight: FontWeight.w500,
          ),
        ),
        subtitle: Text(
          transaction.note.isNotEmpty
              ? '${transaction.note} • ${transaction.createdAt}'
              : transaction.createdAt,
          style: const TextStyle(color: AppColors.subtext, fontSize: 12),
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              '$sign${transaction.amount.toStringAsFixed(0)}₽',
              style: TextStyle(
                color: iconColor,
                fontWeight: FontWeight.bold,
                fontSize: Dimensions.textLg,
              ),
            ),
            const SizedBox(width: Dimensions.sm),
            GestureDetector(
              onTap: onDelete,
              child: const Icon(Icons.delete_outline,
                  color: AppColors.muted, size: 20),
            ),
          ],
        ),
      ),
    );
  }
}