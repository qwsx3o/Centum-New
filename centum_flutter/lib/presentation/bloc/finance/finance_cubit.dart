import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:centum/data/models/transaction.dart';
import 'package:centum/data/repositories/transaction_repository.dart';
import 'package:centum/domain/services/finance_service.dart';
import 'package:centum/presentation/bloc/finance/finance_state.dart';

class FinanceCubit extends Cubit<FinanceState> {
  final FinanceService service;

  FinanceCubit() : service = FinanceService(), super(FinanceState());

  Future<void> loadSummary() async {
    try {
      emit(state.copyWith(isLoading: true, clearError: true));
      final summary = await service.getSummary();
      final pieData = await service.getPieChartData();
      emit(state.copyWith(
        summary: summary,
        pieData: pieData,
        isLoading: false,
      ));
    } catch (e) {
      emit(state.copyWith(
        isLoading: false,
        error: e.toString(),
      ));
    }
  }

  Future<void> loadHistory({int limit = 100}) async {
    try {
      final history = await service.getHistory(limit: limit);
      emit(state.copyWith(history: history));
    } catch (e) {
      emit(state.copyWith(error: e.toString()));
    }
  }

  Future<void> loadMonthly(int year, int month) async {
    try {
      emit(state.copyWith(isLoading: true, clearError: true));
      final results = await Future.wait([
        TransactionRepository.getMonthlySummary(year, month),
        TransactionRepository.getDaysWithTransactions(year, month),
        TransactionRepository.getTransactionsForMonth(year, month),
      ]);
      emit(state.copyWith(
        monthlySummary: results[0] as MonthlySummary,
        dayGroups: results[1] as List<DayGroup>,
        monthlyTransactions: results[2] as List<Transaction>,
        selectedYear: year,
        selectedMonth: month,
        isLoading: false,
      ));
    } catch (e) {
      emit(state.copyWith(
        isLoading: false,
        error: e.toString(),
      ));
    }
  }

  Future<void> navigateMonth(int direction) async {
    int year = state.selectedYear;
    int month = state.selectedMonth + direction;
    if (month > 12) {
      month = 1;
      year++;
    } else if (month < 1) {
      month = 12;
      year--;
    }
    await loadMonthly(year, month);
  }

  Future<void> addIncome(
    double amount,
    int categoryId, {
    String note = '',
  }) async {
    try {
      await service.addIncome(amount, categoryId, note: note);
      await loadSummary();
    } catch (e) {
      emit(state.copyWith(error: e.toString()));
    }
  }

  Future<void> addExpense(
    double amount,
    int categoryId, {
    String note = '',
  }) async {
    try {
      await service.addExpense(amount, categoryId, note: note);
      await loadSummary();
    } catch (e) {
      emit(state.copyWith(error: e.toString()));
    }
  }

  Future<void> deleteTransaction(int id) async {
    try {
      await service.deleteTransaction(id);
      await loadHistory();
      if (state.monthlySummary != null) {
        await loadMonthly(state.selectedYear, state.selectedMonth);
      }
    } catch (e) {
      emit(state.copyWith(error: e.toString()));
    }
  }

  Future<void> refresh() async {
    await Future.wait([
      loadSummary(),
      loadHistory(),
    ]);
  }
}