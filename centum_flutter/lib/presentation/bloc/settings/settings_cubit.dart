import 'package:flutter_bloc/flutter_bloc.dart';
import 'settings_state.dart';
import '../../../domain/services/settings_service.dart';

class SettingsCubit extends Cubit<SettingsState> {
  final SettingsService _service;

  SettingsCubit() : _service = SettingsService(), super(const SettingsState());

  Future<void> loadSettings() async {
    emit(state.copyWith(isLoading: true));
    try {
      final settings = await _service.loadSettings();
      emit(state.copyWith(settings: settings, isLoading: false));
    } catch (e) {
      emit(state.copyWith(error: e.toString(), isLoading: false));
    }
  }

  Future<void> updateSettings(String key1, String key2, dynamic value) async {
    try {
      await _service.updateSettings(key1, key2, value);
      final settings = await _service.loadSettings();
      emit(state.copyWith(settings: settings));
    } catch (e) {
      emit(state.copyWith(error: e.toString()));
    }
  }

  Future<void> saveNow() async {
    try {
      await _service.saveNow();
    } catch (e) {
      emit(state.copyWith(error: e.toString()));
    }
  }
}