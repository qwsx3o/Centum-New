import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:centum/presentation/bloc/finance/finance_cubit.dart';
import 'package:centum/presentation/bloc/finance/finance_state.dart';
import 'package:centum/core/theme/app_theme.dart';
import 'package:centum/core/constants/dimensions.dart';
import 'package:centum/presentation/views/chronicle/widgets/month_navigator.dart';
import 'package:centum/presentation/views/chronicle/widgets/day_group.dart';

class ChronicleScreen extends StatelessWidget {
  const ChronicleScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: BlocBuilder<FinanceCubit, FinanceState>(
        builder: (context, state) {
          final now = DateTime.now();
          final canGoForward = state.selectedYear < now.year ||
              (state.selectedYear == now.year &&
                  state.selectedMonth < now.month);

          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Padding(
                padding: EdgeInsets.fromLTRB(Dimensions.md, Dimensions.md, 0, 0),
                child: Text(
                  'Хроника',
                  style: TextStyle(
                    fontSize: Dimensions.textXxl,
                    fontWeight: FontWeight.bold,
                    color: AppColors.text,
                  ),
                ),
              ),
              MonthNavigator(
                year: state.selectedYear,
                month: state.selectedMonth,
                canGoForward: canGoForward,
                onPrevious: () =>
                    context.read<FinanceCubit>().navigateMonth(-1),
                onNext: () =>
                    context.read<FinanceCubit>().navigateMonth(1),
              ),
              if (state.isLoading)
                const Expanded(
                  child: Center(child: CircularProgressIndicator()),
                )
              else ...[
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: Dimensions.md),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      _chip('Доход', state.monthlySummary?.income ?? 0, AppColors.income),
                      _chip('Капитал', state.monthlySummary?.capital ?? 0, AppColors.capital),
                      _chip('Расход', state.monthlySummary?.expenses ?? 0, AppColors.expense),
                    ],
                  ),
                ),
                const Divider(color: AppColors.muted, height: Dimensions.lg),
                Expanded(
                  child: state.dayGroups.isEmpty
                      ? Center(
                          child: Text(
                            'Нет операций за этот месяц',
                            style: TextStyle(color: AppColors.subtext),
                          ),
                        )
                      : RefreshIndicator(
                          onRefresh: () async {
                            context.read<FinanceCubit>().loadMonthly(
                              state.selectedYear,
                              state.selectedMonth,
                            );
                          },
                          child: ListView.builder(
                            itemCount: state.dayGroups.length,
                            itemBuilder: (context, index) {
                              return DayGroupWidget(
                                  dayGroup: state.dayGroups[index]);
                            },
                          ),
                        ),
                ),
              ],
            ],
          );
        },
      ),
    );
  }

  Widget _chip(String label, double value, Color color) {
    return Column(
      children: [
        Text(
          '${value.toStringAsFixed(0)}₽',
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.bold,
            fontSize: Dimensions.textLg,
          ),
        ),
        Text(label,
            style: const TextStyle(color: AppColors.subtext, fontSize: 12)),
      ],
    );
  }
}