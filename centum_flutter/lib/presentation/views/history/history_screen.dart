import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:centum/presentation/bloc/finance/finance_cubit.dart';
import 'package:centum/presentation/bloc/finance/finance_state.dart';
import 'package:centum/core/theme/app_theme.dart';
import 'package:centum/core/constants/dimensions.dart';
import 'package:centum/presentation/views/history/widgets/transaction_card.dart';

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.fromLTRB(Dimensions.md, Dimensions.md, 0, 0),
            child: Text(
              'История',
              style: TextStyle(
                fontSize: Dimensions.textXxl,
                fontWeight: FontWeight.bold,
                color: AppColors.text,
              ),
            ),
          ),
          Expanded(
            child: BlocBuilder<FinanceCubit, FinanceState>(
              builder: (context, state) {
                if (state.isLoading) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (state.history.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.receipt_long_outlined,
                            size: 64, color: AppColors.muted),
                        const SizedBox(height: Dimensions.md),
                        Text(
                          'История пуста',
                          style: TextStyle(color: AppColors.subtext),
                        ),
                      ],
                    ),
                  );
                }
                return RefreshIndicator(
                  onRefresh: () async {
                    context.read<FinanceCubit>().loadHistory();
                  },
                  child: ListView.builder(
                    padding: const EdgeInsets.all(Dimensions.md),
                    itemCount: state.history.length,
                    itemBuilder: (context, index) {
                      final tx = state.history[index];
                      return TransactionCard(
                        transaction: tx,
                        onDelete: () => _confirmDelete(context, tx.id),
                      );
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  void _confirmDelete(BuildContext context, int id) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.surface,
        title: const Text('Удалить запись?',
            style: TextStyle(color: AppColors.text)),
        content: const Text('Это действие нельзя отменить.',
            style: TextStyle(color: AppColors.subtext)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Отмена',
                style: TextStyle(color: AppColors.subtext)),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              context.read<FinanceCubit>().deleteTransaction(id);
            },
            child: const Text('Удалить',
                style: TextStyle(color: AppColors.expense)),
          ),
        ],
      ),
    );
  }
}