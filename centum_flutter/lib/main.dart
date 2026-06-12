import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'app.dart';
import 'core/theme/app_theme.dart';
import 'presentation/bloc/finance/finance_cubit.dart';
import 'presentation/bloc/settings/settings_cubit.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const CentumApp());
}

class CentumApp extends StatelessWidget {
  const CentumApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(create: (_) => FinanceCubit()..refresh()),
        BlocProvider(create: (_) => SettingsCubit()..loadSettings()),
      ],
      child: MaterialApp(
        title: 'Centum',
        debugShowCheckedModeBanner: false,
        theme: buildDarkTheme(),
        home: const AppRouter(),
      ),
    );
  }
}