import 'package:centum/data/models/transaction.dart';

class FinanceState {
  final FinanceSummary summary;
  final List<PieSegment> pieData;
  final List<Transaction> history;
  final MonthlySummary? monthlySummary;
  final List<DayGroup> dayGroups;
  final List<Transaction> monthlyTransactions;
  final bool isLoading;
  final String? error;
  final int selectedYear;
  final int selectedMonth;

  FinanceState({
    this.summary = const FinanceSummary(),
    this.pieData = const [],
    this.history = const [],
    this.monthlySummary,
    this.dayGroups = const [],
    this.monthlyTransactions = const [],
    this.isLoading = false,
    this.error,
    int? selectedYear,
    int? selectedMonth,
  })  : selectedYear = selectedYear ?? DateTime.now().year,
        selectedMonth = selectedMonth ?? DateTime.now().month;

  FinanceState copyWith({
    FinanceSummary? summary,
    List<PieSegment>? pieData,
    List<Transaction>? history,
    MonthlySummary? monthlySummary,
    List<DayGroup>? dayGroups,
    List<Transaction>? monthlyTransactions,
    bool? isLoading,
    String? error,
    bool clearError = false,
    int? selectedYear,
    int? selectedMonth,
  }) {
    return FinanceState(
      summary: summary ?? this.summary,
      pieData: pieData ?? this.pieData,
      history: history ?? this.history,
      monthlySummary: monthlySummary ?? this.monthlySummary,
      dayGroups: dayGroups ?? this.dayGroups,
      monthlyTransactions: monthlyTransactions ?? this.monthlyTransactions,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      selectedYear: selectedYear ?? this.selectedYear,
      selectedMonth: selectedMonth ?? this.selectedMonth,
    );
  }
}