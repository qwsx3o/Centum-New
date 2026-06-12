import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:centum/presentation/bloc/finance/finance_cubit.dart';
import 'package:centum/presentation/bloc/finance/finance_state.dart';
import 'package:centum/presentation/views/main/widgets/donut_chart.dart';
import 'package:centum/presentation/views/main/widgets/statistic_chip.dart';
import 'package:centum/presentation/components/add_income_dialog.dart';
import 'package:centum/presentation/components/add_expense_dialog.dart';
import 'package:centum/core/theme/app_theme.dart';
import 'package:centum/core/constants/dimensions.dart';
import 'package:centum/data/models/transaction.dart';

class MainScreen extends StatelessWidget {
  const MainScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: BlocBuilder<FinanceCubit, FinanceState>(
        builder: (context, state) {
          if (state.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state.error != null) {
            return Center(
              child: Text(state.error!, style: const TextStyle(color: AppColors.expense)),
            );
          }

          final summary = state.summary;
          final pieData = state.pieData;

          return SingleChildScrollView(
            padding: const EdgeInsets.all(Dimensions.md),
            child: Column(
              children: [
                const Text(
                  'CENTUM',
                  style: TextStyle(
                    fontSize: Dimensions.textXxl,
                    fontWeight: FontWeight.bold,
                    color: AppColors.accent,
                    letterSpacing: 8,
                  ),
                ),
                const SizedBox(height: Dimensions.lg),
                DonutChart(
                  segments: pieData,
                  centerLabel: '${summary.totalIncome.toStringAsFixed(0)}₽',
                  centerSubLabel: 'общий доход',
                ),
                const SizedBox(height: Dimensions.lg),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    StatisticChip(
                      label: 'Капитал',
                      value: '${summary.totalCapital.toStringAsFixed(0)}₽',
                      color: AppColors.capital,
                    ),
                    StatisticChip(
                      label: 'Доступно',
                      value: '${summary.available.toStringAsFixed(0)}₽',
                      color: AppColors.available,
                    ),
                    StatisticChip(
                      label: 'Траты',
                      value: '${summary.totalExpenses.toStringAsFixed(0)}₽',
                      color: AppColors.expense,
                    ),
                  ],
                ),
                const SizedBox(height: Dimensions.md),
                ...pieData.map((seg) => _buildLegendRow(seg)),
                const Spacer(),
                const SizedBox(height: Dimensions.lg),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => _showIncomeDialog(context),
                        icon: const Icon(Icons.add_circle_outline,
                            color: AppColors.income),
                        label: const Text('+ Доход',
                            style: TextStyle(color: AppColors.income)),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.income.withOpacity(0.1),
                        ),
                      ),
                    ),
                    const SizedBox(width: Dimensions.md),
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => _showExpenseDialog(context),
                        icon: const Icon(Icons.remove_circle_outline,
                            color: AppColors.expense),
                        label: const Text('- Расход',
                            style: TextStyle(color: AppColors.expense)),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.expense.withOpacity(0.1),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: Dimensions.md),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildLegendRow(PieSegment seg) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              color: Color(int.parse(seg.color.replaceFirst('#', '0xFF'))),
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(width: Dimensions.sm),
          Text(seg.label, style: const TextStyle(color: AppColors.subtext)),
          const Spacer(),
          Text('${seg.value.toStringAsFixed(0)}₽',
              style: const TextStyle(color: AppColors.text)),
        ],
      ),
    );
  }

  void _showIncomeDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => BlocProvider.value(
        value: BlocProvider.of<FinanceCubit>(context),
        child: const AddIncomeDialog(),
      ),
    );
  }

  void _showExpenseDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => BlocProvider.value(
        value: BlocProvider.of<FinanceCubit>(context),
        child: const AddExpenseDialog(),
      ),
    );
  }
}