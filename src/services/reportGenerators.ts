import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';
import { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, HeadingLevel } from 'docx';
import saveAs from 'file-saver';
import { 
  AgriculturalField, 
  ManagementZone, 
  RLDecision, 
  SensorTelemetry, 
  AuditLogEntry 
} from '../types';

export interface ReportGenerationPayload {
  field: AgriculturalField;
  zones: ManagementZone[];
  sensors: SensorTelemetry[];
  decisions: RLDecision[];
  auditLogs: AuditLogEntry[];
  generatedBy: string;
}

/**
 * Generates an executive PDF Report with jsPDF and autoTable
 */
export function generateExecutivePDF(data: ReportGenerationPayload): void {
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'
  });

  const primaryColor: [number, number, number] = [16, 185, 129]; // Emerald 500
  const darkColor: [number, number, number] = [15, 23, 42];      // Slate 900
  const grayColor: [number, number, number] = [100, 116, 139];   // Slate 500

  // Header Banner
  doc.setFillColor(...darkColor);
  doc.rect(0, 0, 210, 32, 'F');

  doc.setTextColor(255, 255, 255);
  doc.setFontSize(16);
  doc.setFont('helvetica', 'bold');
  doc.text('AGRO-PRECISION DIGITAL TWIN VRI', 14, 14);

  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(167, 243, 208); // Emerald 200
  doc.text('Closed-Loop Autonomous Variable-Rate Irrigation System | Executive Agronomic Report', 14, 22);

  doc.setFontSize(8);
  doc.setTextColor(203, 213, 225);
  doc.text(`Fecha: ${new Date().toLocaleString('es-PE')} | Generado por: ${data.generatedBy}`, 14, 28);

  // Field Info Block
  let currentY = 40;
  doc.setTextColor(...darkColor);
  doc.setFontSize(12);
  doc.setFont('helvetica', 'bold');
  doc.text(`Campo: ${data.field.name}`, 14, currentY);

  currentY += 6;
  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(...grayColor);
  doc.text(`Cultivo: ${data.field.cropName} (${data.field.cropVariety}) | Etapa: ${data.field.cropStage.toUpperCase()} (Kc: ${data.field.kcFactor}) | Área: ${data.field.totalAreaHa} Ha`, 14, currentY);

  currentY += 5;
  doc.text(`Sistema de Riego: ${data.field.irrigationSystemType.toUpperCase()} | Ahorro Hídrico Acumulado: ${data.field.waterSavedM3Season.toLocaleString()} m³ | Energía Ahorrada: ${data.field.energySavedKwhSeason.toLocaleString()} kWh`, 14, currentY);

  // KPI Summary Table
  currentY += 6;
  autoTable(doc, {
    startY: currentY,
    head: [['Zona de Manejo', 'Textura', 'Área (Ha)', 'Humedad (10/30cm)', 'Temp Dosel (°C)', 'CWSI Estrés', 'Dosis RL (mm)', 'Volumen (m³)']],
    body: data.zones.map(z => [
      z.name,
      z.soilTexture.replace('_', ' '),
      z.areaHectares.toFixed(1),
      `${z.currentMoisture10cm}% / ${z.currentMoisture30cm}%`,
      `${z.currentCanopyTemp}°C`,
      z.cwsi.toFixed(2),
      `${z.recommendedRateMm} mm`,
      `${Math.round((z.recommendedRateMm / 1000) * z.areaHectares * 10000)} m³`
    ]),
    theme: 'grid',
    headStyles: { fillColor: primaryColor, textColor: 255, fontStyle: 'bold', fontSize: 8 },
    bodyStyles: { fontSize: 8, textColor: 30 },
    alternateRowStyles: { fillColor: [248, 250, 252] }
  });

  // Recent RL Decisions Table
  // @ts-ignore
  currentY = doc.lastAutoTable.finalY + 10;
  doc.setTextColor(...darkColor);
  doc.setFontSize(11);
  doc.setFont('helvetica', 'bold');
  doc.text('Registro de Decisiones del Agente RL y Explicabilidad (XAI)', 14, currentY);

  currentY += 4;
  autoTable(doc, {
    startY: currentY,
    head: [['ID Decisión', 'Zona', 'Dosis (mm)', 'Confianza', 'Estado', 'Característica Dominante (XAI)']],
    body: data.decisions.map(d => [
      d.id,
      d.zoneName,
      `${d.recommendedDepthMm} mm`,
      `${Math.round(d.confidenceScore * 100)}%`,
      d.status.toUpperCase(),
      d.explanation.dominantFeature
    ]),
    theme: 'striped',
    headStyles: { fillColor: darkColor, textColor: 255, fontStyle: 'bold', fontSize: 8 },
    bodyStyles: { fontSize: 7.5, textColor: 40 }
  });

  // Footer Signatures
  // @ts-ignore
  const finalY = Math.min(270, doc.lastAutoTable.finalY + 20);
  doc.setDrawColor(200, 200, 200);
  doc.line(20, finalY, 80, finalY);
  doc.line(130, finalY, 190, finalY);

  doc.setFontSize(8);
  doc.setTextColor(...grayColor);
  doc.text('Firma Agrónomo Responsable', 25, finalY + 5);
  doc.text('Firma Validación Digital Twin RL', 135, finalY + 5);

  doc.save(`Reporte_Ejecutivo_Digital_Twin_${data.field.id}_${new Date().toISOString().split('T')[0]}.pdf`);
}

/**
 * Generates an editable Word (.docx) Document
 */
export async function generateWordDocx(data: ReportGenerationPayload): Promise<void> {
  const doc = new Document({
    sections: [
      {
        properties: {},
        children: [
          new Paragraph({
            text: 'INFORME TÉCNICO AGRONÓMICO: GEMELO DIGITAL DE RIEGO VRI',
            heading: HeadingLevel.HEADING_1,
            spacing: { after: 200 }
          }),
          new Paragraph({
            children: [
              new TextRun({ text: `Campo: `, bold: true }),
              new TextRun(`${data.field.name}\n`),
              new TextRun({ text: `Cultivo: `, bold: true }),
              new TextRun(`${data.field.cropName} (${data.field.cropVariety}) - Etapa: ${data.field.cropStage}\n`),
              new TextRun({ text: `Fecha de emisión: `, bold: true }),
              new TextRun(`${new Date().toLocaleString('es-PE')}\n`),
              new TextRun({ text: `Auditor / Ingeniero: `, bold: true }),
              new TextRun(`${data.generatedBy}\n`)
            ],
            spacing: { after: 300 }
          }),
          new Paragraph({
            text: '1. Diagnóstico Hidráulico y Estrés Hídrico por Zona',
            heading: HeadingLevel.HEADING_2,
            spacing: { before: 200, after: 150 }
          }),
          new Table({
            width: { size: 100, type: WidthType.PERCENTAGE },
            rows: [
              new TableRow({
                children: [
                  new TableCell({ children: [new Paragraph({ text: 'Zona', style: 'bold' })] }),
                  new TableCell({ children: [new Paragraph({ text: 'Textura' })] }),
                  new TableCell({ children: [new Paragraph({ text: 'Humedad 10cm' })] }),
                  new TableCell({ children: [new Paragraph({ text: 'Temp Dosel' })] }),
                  new TableCell({ children: [new Paragraph({ text: 'CWSI' })] }),
                  new TableCell({ children: [new Paragraph({ text: 'Recomendación RL' })] })
                ]
              }),
              ...data.zones.map(z => new TableRow({
                children: [
                  new TableCell({ children: [new Paragraph(z.name)] }),
                  new TableCell({ children: [new Paragraph(z.soilTexture)] }),
                  new TableCell({ children: [new Paragraph(`${z.currentMoisture10cm}%`)] }),
                  new TableCell({ children: [new Paragraph(`${z.currentCanopyTemp}°C`)] }),
                  new TableCell({ children: [new Paragraph(z.cwsi.toFixed(2))] }),
                  new TableCell({ children: [new Paragraph(`${z.recommendedRateMm} mm`)] })
                ]
              }))
            ]
          }),
          new Paragraph({
            text: '2. Fundamentación del Modelo de Aprendizaje por Refuerzo (RL)',
            heading: HeadingLevel.HEADING_2,
            spacing: { before: 300, after: 150 }
          }),
          new Paragraph({
            text: 'El agente de política de optimización proximal (PPO) analiza conjuntamente la humedad volumétrica del suelo en múltiples estratos, la termografía infrarroja del dosel (CWSI) y los ecos de reflectividad del radar meteorológico para evitar riegos redundantes. Se minimiza el consumo hídrico y se garantiza que el bulbo húmedo no sobrepase la capacidad de campo.',
            spacing: { after: 200 }
          }),
          new Paragraph({
            text: '3. Registro de Auditoría y Trazabilidad',
            heading: HeadingLevel.HEADING_2,
            spacing: { before: 200, after: 150 }
          }),
          ...data.auditLogs.map(l => new Paragraph({
            children: [
              new TextRun({ text: `[${l.timestamp.split('T')[1].split('.')[0]}] `, bold: true }),
              new TextRun({ text: `${l.userRole.toUpperCase()} (${l.userEmail}): `, color: '2563EB' }),
              new TextRun(`${l.action} - ${l.details}`)
            ],
            spacing: { after: 80 }
          }))
        ]
      }
    ]
  });

  const blob = await Packer.toBlob(doc);
  saveAs(blob, `Informe_Agronomico_VRI_${data.field.id}_${new Date().toISOString().split('T')[0]}.docx`);
}

/**
 * Generates a Multi-Tab Excel (.xlsx) Workbook
 */
export function generateExcelWorkbook(data: ReportGenerationPayload): void {
  const wb = XLSX.utils.book_new();

  // Tab 1: Resumen General
  const resumenData = [
    ['CAMPO AGRÍCOLA', data.field.name],
    ['CULTIVO', data.field.cropName],
    ['VARIEDAD', data.field.cropVariety],
    ['ETAPA FENOLÓGICA', data.field.cropStage],
    ['COEFICIENTE Kc (FAO-56)', data.field.kcFactor],
    ['ÁREA TOTAL (Ha)', data.field.totalAreaHa],
    ['SISTEMA DE RIEGO', data.field.irrigationSystemType],
    ['AHORRO HÍDRICO ACUMULADO (m3)', data.field.waterSavedM3Season],
    ['AHORRO ENERGÉTICO (kWh)', data.field.energySavedKwhSeason],
    ['FECHA DE REPORTE', new Date().toISOString()]
  ];
  const wsResumen = XLSX.utils.aoa_to_sheet(resumenData);
  XLSX.utils.book_append_sheet(wb, wsResumen, 'Resumen_Campo');

  // Tab 2: Zonas de Manejo
  const zonasData = data.zones.map(z => ({
    'ID Zona': z.id,
    'Nombre': z.name,
    'Área (Ha)': z.areaHectares,
    'Textura Suelo': z.soilTexture,
    'Capacidad Campo (m3/m3)': z.fieldCapacity,
    'Punto Marchitez (m3/m3)': z.wiltingPoint,
    'Conductividad Ksat (mm/h)': z.saturatedK,
    'Humedad 10cm (%)': z.currentMoisture10cm,
    'Humedad 30cm (%)': z.currentMoisture30cm,
    'Humedad 60cm (%)': z.currentMoisture60cm,
    'Temp Dosel (°C)': z.currentCanopyTemp,
    'CWSI Estrés': z.cwsi,
    'Dosis RL (mm)': z.recommendedRateMm,
    'Volumen m3': Math.round((z.recommendedRateMm / 1000) * z.areaHectares * 10000),
    'Eficiencia Hidráulica': z.hydraulicEfficiency,
    'Estado': z.status
  }));
  const wsZonas = XLSX.utils.json_to_sheet(zonasData);
  XLSX.utils.book_append_sheet(wb, wsZonas, 'Zonas_Manejo');

  // Tab 3: Telemetría de Sensores
  const sensoresData = data.sensors.map(s => ({
    'ID Sensor': s.sensorId,
    'Tipo': s.sensorType,
    'Zona': s.zoneId,
    'Latitud': s.location.lat,
    'Longitud': s.location.lng,
    'Estado': s.status,
    'Batería (%)': s.batteryLevel,
    'RSSI (dBm)': s.rssi,
    'Humedad 10cm (%)': s.readings.volumetricWaterContent_10cm ?? 'N/A',
    'Humedad 30cm (%)': s.readings.volumetricWaterContent_30cm ?? 'N/A',
    'Humedad 60cm (%)': s.readings.volumetricWaterContent_60cm ?? 'N/A',
    'Temp Dosel (°C)': s.readings.canopyTemperatureC ?? 'N/A',
    'Temp Aire (°C)': s.readings.ambientAirTempC ?? 'N/A',
    'Humedad Relativa (%)': s.readings.relativeHumidityPct ?? 'N/A',
    'Calidad Dato (0-100)': s.qualityScore
  }));
  const wsSensores = XLSX.utils.json_to_sheet(sensoresData);
  XLSX.utils.book_append_sheet(wb, wsSensores, 'Telemetria_Sensores');

  // Tab 4: Decisiones RL y XAI
  const decisionesData = data.decisions.map(d => ({
    'ID Decisión': d.id,
    'Zona': d.zoneName,
    'Timestamp': d.timestamp,
    'Política RL': d.policyId,
    'Dosis Recomendada (mm)': d.recommendedDepthMm,
    'Volumen (m3)': d.recommendedVolumeM3,
    'Confianza': d.confidenceScore,
    'Estado': d.status,
    'Aprobado Por': d.approvedBy ?? 'N/A',
    'Recompensa Esperada': d.rewardExpected,
    'XAI Característica Principal': d.explanation.dominantFeature,
    'XAI Razonamiento': d.explanation.reasoningText
  }));
  const wsDecisiones = XLSX.utils.json_to_sheet(decisionesData);
  XLSX.utils.book_append_sheet(wb, wsDecisiones, 'Decisiones_RL');

  // Tab 5: Logs de Auditoría
  const auditData = data.auditLogs.map(a => ({
    'ID': a.id,
    'Timestamp': a.timestamp,
    'Usuario Email': a.userEmail,
    'Rol': a.userRole,
    'Acción': a.action,
    'Recurso': a.resource,
    'Detalles': a.details,
    'IP Cliente': a.clientIp,
    'Firma SHA256': a.sha256Signature
  }));
  const wsAudit = XLSX.utils.json_to_sheet(auditData);
  XLSX.utils.book_append_sheet(wb, wsAudit, 'Auditoria_RBAC');

  XLSX.writeFile(wb, `Digital_Twin_VRI_Dataset_${data.field.id}_${new Date().toISOString().split('T')[0]}.xlsx`);
}

/**
 * Generates Raw CSV Export
 */
export function generateCSVExport(data: ReportGenerationPayload): void {
  const rows = [
    ['sensor_id', 'zone_id', 'timestamp', 'moisture_10cm', 'moisture_30cm', 'moisture_60cm', 'canopy_temp_c', 'ambient_temp_c', 'cwsi', 'quality_score'],
    ...data.sensors.map(s => [
      s.sensorId,
      s.zoneId,
      s.timestamp,
      s.readings.volumetricWaterContent_10cm ?? '',
      s.readings.volumetricWaterContent_30cm ?? '',
      s.readings.volumetricWaterContent_60cm ?? '',
      s.readings.canopyTemperatureC ?? '',
      s.readings.ambientAirTempC ?? '',
      data.zones.find(z => z.id === s.zoneId)?.cwsi ?? '',
      s.qualityScore
    ])
  ];

  const csvContent = rows.map(r => r.join(',')).join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  saveAs(blob, `Telemetria_Raw_${data.field.id}_${new Date().toISOString().split('T')[0]}.csv`);
}

/**
 * Generates JSON Export
 */
export function generateJSONExport(data: ReportGenerationPayload): void {
  const jsonContent = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' });
  saveAs(blob, `Digital_Twin_State_Full_${data.field.id}_${new Date().toISOString().split('T')[0]}.json`);
}
