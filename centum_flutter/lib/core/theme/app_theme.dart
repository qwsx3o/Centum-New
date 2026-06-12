import 'package:flutter/material.dart';
import 'package:centum/core/constants/dimensions.dart';

class AppColors {
  static const Color bg = Color(0xFF0D0D0D);
  static const Color surface = Color(0xFF1A1A1A);
  static const Color card = Color(0xFF242424);
  static const Color accent = Color(0xFFC9A84C);
  static const Color capital = Color(0xFFC9A84C);
  static const Color income = Color(0xFF4CAF50);
  static const Color expense = Color(0xFFEF5350);
  static const Color available = Color(0xFF42A5F5);
  static const Color text = Color(0xFFF5F5F5);
  static const Color subtext = Color(0xFF9E9E9E);
  static const Color muted = Color(0xFF555555);
  static const Color warmBg = Color(0xFF1A1500);
}

ThemeData buildDarkTheme() {
  return ThemeData(
    brightness: Brightness.dark,
    scaffoldBackgroundColor: AppColors.bg,
    colorScheme: const ColorScheme.dark(
      primary: AppColors.accent,
      surface: AppColors.surface,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: AppColors.bg,
      elevation: 0,
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: AppColors.surface,
      indicatorColor: AppColors.accent.withOpacity(0.2),
      labelTextStyle: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const TextStyle(color: AppColors.accent, fontSize: 12);
        }
        return const TextStyle(color: AppColors.subtext, fontSize: 12);
      }),
      iconTheme: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const IconThemeData(color: AppColors.accent);
        }
        return const IconThemeData(color: AppColors.subtext);
      }),
    ),
    snackBarTheme: const SnackBarThemeData(
      backgroundColor: AppColors.card,
      contentTextStyle: TextStyle(color: AppColors.text),
      behavior: SnackBarBehavior.floating,
    ),
    dialogTheme: const DialogThemeData(
      backgroundColor: AppColors.surface,
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.card,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(Dimensions.radiusSm),
        borderSide: BorderSide.none,
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(Dimensions.radiusSm),
        borderSide: const BorderSide(color: AppColors.accent),
      ),
      labelStyle: const TextStyle(color: AppColors.subtext),
      hintStyle: const TextStyle(color: AppColors.muted),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(Dimensions.radiusSm),
        ),
        padding: const EdgeInsets.symmetric(
          horizontal: Dimensions.lg,
          vertical: Dimensions.md,
        ),
      ),
    ),
    textTheme: const TextTheme(
      headlineLarge: TextStyle(
        fontSize: Dimensions.textHero,
        fontWeight: FontWeight.bold,
        color: AppColors.text,
      ),
      headlineMedium: TextStyle(
        fontSize: Dimensions.textXxl,
        fontWeight: FontWeight.bold,
        color: AppColors.text,
      ),
      titleLarge: TextStyle(
        fontSize: Dimensions.textXl,
        fontWeight: FontWeight.w600,
        color: AppColors.text,
      ),
      titleMedium: TextStyle(
        fontSize: Dimensions.textLg,
        fontWeight: FontWeight.w500,
        color: AppColors.text,
      ),
      bodyLarge: TextStyle(
        fontSize: Dimensions.textMd,
        color: AppColors.text,
      ),
      bodyMedium: TextStyle(
        fontSize: Dimensions.textSm,
        color: AppColors.subtext,
      ),
      labelSmall: TextStyle(
        fontSize: Dimensions.textXs,
        color: AppColors.muted,
      ),
    ),
  );
}