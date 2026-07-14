%% =====================================================================
%% RAYTRACING HETNET (MICRO gNB + MICRO gNB) PARA 6 DRONES
%% =====================================================================
clear all; clc;

try
    close(siteviewer); 
catch
end

%% 1. PARÁMETROS DE CONFIGURACIÓN
fc = 3.5e9;              % Frecuencia 3.5 GHz (Banda n78)
reflectionsOrder = 2;    % Dos rebotes de rayos

% --- CONFIGURACIÓN DE LAS gNB (Red Heterogénea / HetNet) ---
% Índice 1: Microcelda (Techo alto, cubre todo el campus)
% Índice 2: Microcelda (Small cell baja para el patio de sombra)
txLat     = [-2.891264, -2.891652];  
txLon     = [-79.037817, -79.035577]; 
txHeight  = [7, 7];     % Alturas en metros sobre los edificios
txAzimuth = [120, 270];  % La microcelda apunta hacia el oeste (patio interior)
txTilt    = [-2, 0];     

% --- CONFIGURACIÓN DE LOS 6 DRONES (UEs) ---
% Coordenadas de los Drones
ueLatitude  = [-2.891087, -2.891767, -2.891582, -2.890918, -2.892232, -2.890947];  
ueLongitude = [-79.038321, -79.038238, -79.037592, -79.036202, -79.036551, -79.035033]; 
ueHeight    = [30, 30, 30, 30, 10, 10]; 

ueAzimuth   = 0;
ueTilt      = 0;
numUEs      = length(ueLatitude); 

%% 2. VISUALIZACIÓN DEL ENTORNO 3D
viewer = siteviewer("Basemap", "openstreetmap", "Buildings", "map.osm");

%% 3. CREACIÓN DE LOS SITIOS (2 Tx y 6 Rx)
bsSite1 = txsite("Name", "Macro gNB Central", ...
    "Latitude", txLat(1), "Longitude", txLon(1), ...
    "AntennaAngle", [txAzimuth(1); txTilt(1)], ... 
    "AntennaHeight", txHeight(1), ...
    "TransmitterFrequency", fc);

bsSite2 = txsite("Name", "Micro gNB Patio", ...
    "Latitude", txLat(2), "Longitude", txLon(2), ...
    "AntennaAngle", [txAzimuth(2); txTilt(2)], ... 
    "AntennaHeight", txHeight(2), ...
    "TransmitterFrequency", fc);

allBSSites = [bsSite1; bsSite2]; % Agrupamos ambas antenas

ueSite = rxsite("Name", "Dron Patrulla", ...
    "Latitude", ueLatitude, "Longitude", ueLongitude, ...
    "AntennaHeight", ueHeight);

allBSSites.show();
ueSite.show();

%% 4. CONFIGURACIÓN Y PROCESAMIENTO DEL RAYTRACING
pm = propagationModel("raytracing", ...
                      "Method", "sbr", ...
                      "MaxNumReflections", reflectionsOrder);

fprintf('Calculando propagacion Multi-Sitio (HetNet) para los 6 drones...\n');
% Al tener 2 Tx y 6 Rx, MATLAB genera una matriz de rayos 2x6
rays = raytrace(allBSSites, ueSite, pm, "Type", "pathloss");

%% =====================================================================
%% 5. ANÁLISIS DE SELECCIÓN DE CELDA Y MODELADO DE CANAL
%% =====================================================================
c = physconst('LightSpeed');
lambda = c/fc;
bsAntSize = [4 4]; 
ueAntSize = [2 2]; 

fprintf('\n================ INFORME DE RED HETEROGÉNEA (6 DRONES) ================\n');

for i = 1:numUEs
    % --- LÓGICA DE SELECCIÓN DE CELDA (HANDOVER) ---
    % Comparamos los rayos recibidos desde la Micro (Tx1) y la Micro (Tx2)
    raysTx1 = rays{1, i};
    raysTx2 = rays{2, i};
    
    pl1 = inf; pl2 = inf;
    if ~isempty(raysTx1), pl1 = min([raysTx1.PathLoss]); end
    if ~isempty(raysTx2), pl2 = min([raysTx2.PathLoss]); end
    
    % El dron se conecta a la gNB con la menor pérdida (Path Loss)
    if pl1 <= pl2
        best_rays = raysTx1;
        best_tx_idx = 1;
        serving_gnb = "Macro gNB Central";
    else
        best_rays = raysTx2;
        best_tx_idx = 2;
        serving_gnb = "Micro gNB Patio (Small Cell)";
    end
    
    fprintf('\n[DRON %d] -> Altura: %d m | Conectado a: %s\n', i, ueHeight(i), serving_gnb);
    
    if ~isempty(best_rays) && min([best_rays.PathLoss]) < 130
        % Graficar en el mapa solo los rayos de la gNB ganadora
        plot(best_rays);
        
        isLOS = any([best_rays.LineOfSight]);
        fprintf('  - ¿Línea de Vista (LOS)?: %d\n', isLOS);
        fprintf('  - Número de Rayos: %d\n', length(best_rays));
        fprintf('  - Pérdida (Path Loss) del enlace: %.2f dB\n', min([best_rays.PathLoss]));
        
        % Extracción para CDL
        pathToAs = [best_rays.PropagationDelay] - min([best_rays.PropagationDelay]); 
        avgPathGains = -[best_rays.PathLoss]; 
        pathAoDs = [best_rays.AngleOfDeparture]; 
        pathAoAs = [best_rays.AngleOfArrival]; 
        
        % --- CONFIGURACIÓN DE CANAL 3GPP CDL ---
        channel = nrCDLChannel;
        channel.DelayProfile = 'Custom';
        channel.PathDelays = pathToAs;
        channel.AveragePathGains = avgPathGains;
        channel.AnglesAoD = pathAoDs(1,:);        
        channel.AnglesZoD = 90 - pathAoDs(2,:);   
        channel.AnglesAoA = pathAoAs(1,:);        
        channel.AnglesZoA = 90 - pathAoAs(2,:);   
        channel.HasLOSCluster = isLOS;
        channel.CarrierFrequency = fc;
        channel.NormalizeChannelOutputs = false;  
        channel.NormalizePathGains = false;
        
        % Antenas MIMO
        ueArray = phased.NRRectangularPanelArray('Size', [ueAntSize(1:2) 1 1], 'Spacing', [0.5*lambda*[1 1] 1 1]);
        channel.ReceiveAntennaArray = ueArray;
        channel.ReceiveArrayOrientation = [ueAzimuth; (-1)*ueTilt; 0];
        
        bsArray = phased.NRRectangularPanelArray('Size', [bsAntSize(1:2) 1 1], 'Spacing', [0.5*lambda*[1 1] 1 1]);
        bsArray.ElementSet = {phased.NRAntennaElement('PolarizationAngle',-45) phased.NRAntennaElement('PolarizationAngle',45)};
        channel.TransmitAntennaArray = bsArray;
        channel.TransmitArrayOrientation = [txAzimuth(best_tx_idx); (-1)*txTilt(best_tx_idx); 0];
        
        % Procesamiento Baseband simulado
        ofdmInfo = nrOFDMInfo(51, 30);
        channel.SampleRate = ofdmInfo.SampleRate;
        T = channel.SampleRate * 1e-3; 
        numTxElements = prod(bsAntSize) * 2; 
        txSig = complex(randn(T, numTxElements), randn(T, numTxElements));
        
        try
            [~, pathGains, sampleTimes] = channel(txSig);
            pathFilters = getPathFilters(channel);
            [offset,~] = nrPerfectTimingEstimate(pathGains,pathFilters);
            hest = nrPerfectChannelEstimate(pathGains,pathFilters,51,30,0,offset,sampleTimes);
            [wbs, ~, ~] = getBeamformingWeights(hest, 1, 0, 1);
        catch
            fprintf('  - Alerta: Falla en decodificacion MIMO (Multicamino extremo).\n');
        end
    else
        fprintf('  - ALERTA ROJA: Dron en zona de sombra absoluta o señal muy débil.\n');
    end
end
fprintf('\n===========================================================================\n');

%% =====================================================================
%% FUNCIONES AUXILIARES (Helper Functions)
%% =====================================================================
function [wT, wR, mag] = getBeamformingWeights(hEst, nLayers, scOffset, noRBs)
    scPerRB = 12;
    H = hEst(scOffset + (1:noRBs*scPerRB), 1, :, :);
    H = squeeze(mean(H, 1));
    if iscolumn(H) && size(hEst,3) == 1
        H = H.';
    end
    [U, S, V] = svd(H);
    wT = V(:, 1:nLayers);         
    wR = U(:, 1:nLayers)';        
    mag = diag(S(1:nLayers, 1:nLayers));
end
