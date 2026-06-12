import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:centum/presentation/bloc/finance/finance_cubit.dart';
import 'package:centum/presentation/bloc/settings/settings_cubit.dart';
import 'package:centum/presentation/views/main/main_screen.dart';
import 'package:centum/presentation/views/history/history_screen.dart';
import 'package:centum/presentation/views/chronicle/chronicle_screen.dart';
import 'package:centum/presentation/views/settings/settings_screen.dart';

class AppRouter extends StatefulWidget {
  const AppRouter({super.key});

  @override
  State<AppRouter> createState() => _AppRouterState();
}

class _AppRouterState extends State<AppRouter> {
  int _currentIndex = 0;

  final _screens = [
    MainScreen(),
    HistoryScreen(),
    ChronicleScreen(),
    SettingsScreen(),
  ];

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  void _loadData() {
    context.read<FinanceCubit>().refresh();
    context.read<FinanceCubit>().loadHistory();
    context.read<SettingsCubit>().loadSettings();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) {
          setState(() => _currentIndex = index);
          if (index == 0) {
            context.read<FinanceCubit>().loadSummary();
          } else if (index == 1) {
            context.read<FinanceCubit>().loadHistory();
          } else if (index == 2) {
            final now = DateTime.now();
            context.read<FinanceCubit>().loadMonthly(now.year, now.month);
          } else if (index == 3) {
            context.read<SettingsCubit>().loadSettings();
          }
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Главная',
          ),
          NavigationDestination(
            icon: Icon(Icons.receipt_long_outlined),
            selectedIcon: Icon(Icons.receipt_long),
            label: 'История',
          ),
          NavigationDestination(
            icon: Icon(Icons.calendar_month_outlined),
            selectedIcon: Icon(Icons.calendar_month),
            label: 'Хроника',
          ),
          NavigationDestination(
            icon: Icon(Icons.settings_outlined),
            selectedIcon: Icon(Icons.settings),
            label: 'Настройки',
          ),
        ],
      ),
    );
  }
}