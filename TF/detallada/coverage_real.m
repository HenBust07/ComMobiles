% =========================================================================
% SIMULACIÓN 5G: COBERTURA Y ANÁLISIS DE INTERFERENCIA (Campus Balzay)
% Versión con antenas TRISECTORIALES realistas (patrón 3GPP TR 38.901)
% =========================================================================
%  Para simular un sitio trisectorial real
% (como los paneles gNB/small cell reales) se necesita un patrón con
% lóbulo principal + relación frente-espalda, que es justo lo que define
% el modelo 3GPP TR 38.901 (Tabla 7.3-1)
% =========================================================================

clear all; clc;

%% 1. Cargar el entorno 3D
disp('Cargando mapa 3D y edificios OSM...');
viewer = siteviewer("Buildings", "map.osm");

%% 2. Definir el patrón de antena sectorial 3GPP TR 38.901
freq      = 3.5e9;  % Frecuencia de operación
phi3dB    = 65;      % Ancho de haz a -3dB en AZIMUT (típico panel urbano/small cell)
theta3dB  = 65;      % Ancho de haz a -3dB en ELEVACIÓN
Am        = 30;      % Atenuación máxima lateral en azimut (relación frente-espalda), dB
SLAv      = 30;      % Atenuación máxima lateral en elevación (side-lobe attenuation), dB
GainMax   = 8;        % Ganancia máxima del elemento, dBi (típico panel small cell 5G)

sectorElem = sectorAntenna3GPP(freq, phi3dB, theta3dB, Am, SLAv, GainMax);

% Visualiza el patrón de UN sector antes de desplegarlo (recomendado):
pattern(sectorElem, freq, -180:180, -90:90, ...
    'CoordinateSystem','polar','Type','powerdb');
title('Patrón de un sector individual (3GPP 38.901)');

%% 3. Definición del sitio "Macro" (en realidad microcelda, edificio bajo)
latMacro = -2.891261;
lonMacro = -79.03778;
alturaMacro = 10;          % m, montada en edificio del campus (altura corta real)

% --- Orientación de los 3 sectores ---
azimutsMacro = [25, 145, 265];   % grados, separación estándar 120°
tiltMacro = 1;   % grados (negativo = uptilt, apunta ligeramente hacia arriba)

macroCell = txsite.empty(0,3);
for k = 1:3
    macroCell(k) = txsite("Name", sprintf("Macro gNB - Sector %d (Az %d°)", k, azimutsMacro(k)), ...
        "Latitude", latMacro, "Longitude", lonMacro, ...
        "AntennaHeight", alturaMacro, ...
        "TransmitterFrequency", freq, ...
        "TransmitterPower", 1, ...                 % ~30 dBm, realista para small cell
        "Antenna", sectorElem, ...
        "AntennaAngle", [azimutsMacro(k); tiltMacro]);
end

%% 4. Definición del sitio "Microcelda" (patio de sombra)
latMicro = -2.891566;
lonMicro = -79.035655;
alturaMicro = 10;

% Se puede rotar el arreglo de sectores un offset arbitrario (p.ej. 60°) si
% la orientación de este edificio respecto al norte es distinta a la del
% sitio Macro, para evitar que los sectores "compitan" en la misma zona.
offsetMicro = 60;
azimutsMicro = mod([30, 150] + offsetMicro, 360);
tiltMicro = 1;

microCell = txsite.empty(0,2);
for k = 1:2
    microCell(k) = txsite("Name", sprintf("Microcelda - Sector %d (Az %d°)", k, azimutsMicro(k)), ...
        "Latitude", latMicro, "Longitude", lonMicro, ...
        "AntennaHeight", alturaMicro, ...
        "TransmitterFrequency", freq, ...
        "TransmitterPower", 1, ...
        "Antenna", sectorElem, ...
        "AntennaAngle", [azimutsMicro(k); tiltMicro]);
end

%% 5. Configurar el motor de trazado de rayos (Ray Tracing)
disp('Configurando modelo de propagación Ray Tracing...');
pm = propagationModel("raytracing", "Method", "sbr", "MaxNumReflections", 2);

% =========================================================================
% ETAPA A: JUSTIFICACIÓN DE LA MICROCELDA (Zonas de Sombra)
% Altura del receptor = perímetro bajo ~15-30 m, vigilancia general ~30-60 m,
% BVLOS ~hasta 120 m según normativa local).
% =========================================================================
alturaDron = 30; % m sobre el suelo

disp('Calculando cobertura solo del sitio Macro (3 sectores)...');
coverage(macroCell, ...
    "PropagationModel", pm, ...
    "SignalStrengths", -110:-85, ...
    "ReceiverAntennaHeight", alturaDron, ...
    "MaxRange", 500);
disp('>> Observa las zonas de sombra en el mapa.');
disp('>> Toma tus capturas y presiona ENTER en la consola para continuar...');
pause;

% =========================================================================
% ETAPA B: ANÁLISIS DE INTERFERENCIA (Solapamiento) — usando sinr()
% =========================================================================
disp('Encendiendo ambos sitios (6 sectores en total) y calculando SINR...');
txs = [macroCell, microCell];   % 6 txsite: 3 sectores x 2 sitios

sinr(txs, ...
    "PropagationModel", pm, ...
    "ReceiverAntennaHeight", alturaDron, ...
    "MaxRange", 500);

disp('Simulación completada con antenas trisectoriales 3GPP 38.901.');

% =========================================================================
% FUNCIÓN LOCAL: Patrón de antena sectorial 3GPP TR 38.901 (Tabla 7.3-1)
% =========================================================================
function elem = sectorAntenna3GPP(freq, phi3dB, theta3dB, Am, SLAv, GainMax)
    % Genera un phased.CustomAntennaElement con el patrón sectorial
    % estándar 3GPP usado para modelar antenas de panel gNB/small cell.
    %
    % freq      : frecuencia de diseño (Hz)
    % phi3dB    : HPBW en azimut (grados), típico 65° (urbano) o 90-105° (rural/small cell)
    % theta3dB  : HPBW en elevación (grados), típico 65°
    % Am        : atenuación máx. lateral en azimut / front-to-back (dB), típico 25-30
    % SLAv      : atenuación máx. lateral en elevación (dB), típico 20-30
    % GainMax   : ganancia máxima del elemento (dBi)

    az = -180:1:180;
    el = -90:1:90;
    [AZ, EL] = meshgrid(az, el);   % filas = elevación, columnas = azimut

    % Patrón horizontal (azimut), Ec. 7.3-1 de TR 38.901
    A_h = -min(12*(AZ/phi3dB).^2, Am);

    % Patrón vertical (elevación), medido desde el boresight (0° = horizonte)
    A_v = -min(12*(EL/theta3dB).^2, SLAv);

    % Combinación 3D del patrón (Ec. 7.3-1, combinación horiz/vert)
    A_total = -min(-(A_h + A_v), Am);
    patternDB = GainMax + A_total;   % Ganancia total en dBi

    freqRange = [freq - 100e6, freq + 100e6];   % +/-100 MHz alrededor de freq

    elem = phased.CustomAntennaElement( ...
        "FrequencyVector", freqRange, ...
        "SpecifyPolarizationPattern", false, ...
        "AzimuthAngles", az, ...
        "ElevationAngles", el, ...
        "MagnitudePattern", patternDB, ...
        "FrequencyResponse", [0 0]);   % dB, plano en ese rango
end
