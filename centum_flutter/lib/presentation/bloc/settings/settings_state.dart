class SettingsState {
  final Map<String, dynamic> settings;
  final bool isLoading;
  final String? error;

  const SettingsState({
    this.settings = const {},
    this.isLoading = false,
    this.error,
  });

  SettingsState copyWith({
    Map<String, dynamic>? settings,
    bool? isLoading,
    String? error,
    bool clearError = false,
  }) {
    return SettingsState(
      settings: settings ?? this.settings,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : error ?? this.error,
    );
  }

  int get familyMembers =>
      (settings['profile']?['family_members'] as int?) ?? 1;

  String get currency =>
      (settings['app']?['currency'] as String?) ?? '₽';
}