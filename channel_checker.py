# -*- coding: utf-8 -*-

__version__ = '1.1.0'
__author__ = 'td.junopark'

import os
import time
import pprint
import traceback
# import DeadlineNukeClient

import nuke

try:
    from PySide6.QtWidgets import (
        QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
        QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
        QLabel, QLineEdit, QSpacerItem, QSizePolicy, QFrame, QGroupBox,
        QPushButton, QComboBox, QSpinBox, QMessageBox, QWidget, QCheckBox, QFileDialog, QMenu
    )
    from PySide6.QtGui import (
        QFont, QColor
    )
    from PySide6.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import (
        QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
        QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
        QLabel, QLineEdit, QSpacerItem, QSizePolicy, QFrame, QGroupBox,
        QPushButton, QComboBox, QSpinBox, QMessageBox, QWidget, QCheckBox, QFileDialog, QMenu
    )
    from PySide2.QtGui import (
        QFont, QColor
    )
    from PySide2.QtCore import Qt


class ChannelChecker(QDialog):
    def __init__(self, node):
        super(ChannelChecker, self).__init__()

        self.selected_node = node
        self.set_vars()
        self.set_widgets()
        self.set_layouts()
        self.connections()
        self.populate_data()
        self.show()
        
    def set_vars(self):
        self.headers = []
        self.table_menu = None
        self.files = []
        self.channels = []
        
    def set_widgets(self):
        self.setWindowTitle('Channel Checker v' + __version__)
        self.setMinimumSize(600, 800)
        self.setWindowFlags(
            self.windowFlags() 
            & ~Qt.WindowType.WindowContextHelpButtonHint 
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowCloseButtonHint
            )
        
        self.main_lb = QLabel('Channel Checker')
        self.main_lb.setFont(QFont('Arial', 20, QFont.Weight.Bold))
        self.main_lb.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.headers = ['Render', 'Channel', 'Data Exists']
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(len(self.headers))
        self.table_widget.setHorizontalHeaderLabels(self.headers)
        
        self.table_widget.setSortingEnabled(True)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_widget.horizontalHeader().setSectionResizeMode(self.headers.index('Render'), QHeaderView.ResizeMode.Fixed)
        self.table_widget.horizontalHeader().setSectionResizeMode(self.headers.index('Channel'), QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(self.headers.index('Data Exists'), QHeaderView.ResizeMode.Fixed)
        self.table_widget.setColumnWidth(self.headers.index('Render'), 60)
        self.table_widget.setColumnWidth(self.headers.index('Data Exists'), 100)
        
        self.h_spacer_1 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.h_spacer_2 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.h_spacer_3 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.h_spacer_4 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.h_spacer_5 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.h_spacer_6 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        self.selected_node_lb = QLabel('Selected Node:')
        self.selected_node_lb.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        self.selected_node_lb.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        
        self.h_divider_1 = QFrame()
        self.h_divider_1.setFrameShape(QFrame.Shape.HLine)
        self.h_divider_1.setFrameShadow(QFrame.Shadow.Sunken)
        
        self.target_lb = QLabel('Target Path')
        self.target_lb.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.target_le = QLineEdit()
        self.target_le.setReadOnly(True)
        self.target_le.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        self.frame_step_lb = QLabel('Frame Step')
        self.frame_step_lb.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.frame_step_sb = QSpinBox()
        self.frame_step_sb.setMinimum(1)
        self.frame_step_sb.setValue(10)
        self.frame_step_sb.setSingleStep(1)
        self.frame_step_sb.setSuffix(' frames')
        self.frame_step_sb.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        self.sequence_ext_lb = QLabel('Sequence Ext')
        self.sequence_ext_lb.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.sequence_ext_cmbx = QComboBox()
        self.sequence_ext_cmbx.addItems(['.exr'])
        
        self.folder_prefix_lb = QLabel(' Folder Prefix')
        self.folder_prefix_lb.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.folder_prefix_le = QLineEdit('OIDN')
        self.folder_prefix_le.setFixedWidth(100)
        self.prefix_example_lb = QLabel('  ex) Beauty -> OIDN_Beauty')
        
        self.run_submitter_lb = QLabel('After Setup')
        self.run_submitter_lb.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.run_submitter_cmbx = QComboBox()
        self.run_submitter_cmbx.addItems(['Nothing', 'Submit'])
        
        self.export_log_lb = QLabel('       Log Path')
        self.export_log_lb.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.export_log_le = QLineEdit()
        self.export_log_btn = QPushButton('...')
        self.export_log_btn.setFixedWidth(30)
        
        self.analyze_btn = QPushButton('Analyze')
        self.setup_btn = QPushButton('Set Nodes')
        
    def set_layouts(self):
        main_layout = QVBoxLayout()

        title_layout = QHBoxLayout()
        title_layout.addWidget(self.main_lb)
        title_layout.addItem(self.h_spacer_1)
        title_layout.addWidget(self.selected_node_lb)
        
        analyze_group = QGroupBox('Analyze Settings')
        analyze_group_layout = QGridLayout()
        analyze_group.setLayout(analyze_group_layout)
        
        frame_step_layout = QHBoxLayout()
        frame_step_layout.addWidget(self.frame_step_sb)
        frame_step_layout.addItem(self.h_spacer_2)
        
        sequence_ext_layout = QHBoxLayout()
        sequence_ext_layout.addWidget(self.sequence_ext_cmbx)
        sequence_ext_layout.addItem(self.h_spacer_3)
        
        analyze_group_layout.addWidget(self.target_lb, 0, 0)
        analyze_group_layout.addWidget(self.target_le, 0, 1)
        analyze_group_layout.addWidget(self.frame_step_lb, 1, 0)
        analyze_group_layout.addLayout(frame_step_layout, 1, 1)
        analyze_group_layout.addWidget(self.sequence_ext_lb, 2, 0)
        analyze_group_layout.addLayout(sequence_ext_layout, 2, 1)
        
        render_group = QGroupBox('Node Settings')
        render_group_layout = QGridLayout()
        render_group.setLayout(render_group_layout)
        folder_prefix_layout = QHBoxLayout()
        folder_prefix_layout.addWidget(self.folder_prefix_le)
        folder_prefix_layout.addWidget(self.prefix_example_lb)
        folder_prefix_layout.addItem(self.h_spacer_4)
        
        submitter_layout = QHBoxLayout()
        submitter_layout.addWidget(self.run_submitter_cmbx)
        submitter_layout.addItem(self.h_spacer_5)
        
        render_group_layout.addWidget(self.folder_prefix_lb, 0, 0)
        render_group_layout.addLayout(folder_prefix_layout, 0, 1)
        render_group_layout.addWidget(self.run_submitter_lb, 1, 0)
        render_group_layout.addLayout(submitter_layout, 1, 1)
    
        self.log_group = QGroupBox('Export Log')
        self.log_group.setCheckable(True)
        self.log_group.setChecked(False)
        log_layout = QHBoxLayout()
        self.log_group.setLayout(log_layout)
        log_layout.addWidget(self.export_log_lb)
        log_layout.addWidget(self.export_log_le)
        log_layout.addWidget(self.export_log_btn)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.analyze_btn)
        button_layout.addItem(self.h_spacer_6)
        button_layout.addWidget(self.setup_btn)
        
        main_layout.addLayout(title_layout)
        main_layout.addWidget(self.h_divider_1)
        main_layout.addWidget(self.table_widget)
        main_layout.addWidget(analyze_group)
        main_layout.addWidget(render_group)
        main_layout.addWidget(self.log_group)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
    def connections(self):
        self.folder_prefix_le.textChanged.connect(self.update_folder_prefix)
        self.table_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.export_log_btn.clicked.connect(self.browse_log_path)
        self.analyze_btn.clicked.connect(self.analyze_handler)
        self.setup_btn.clicked.connect(self.setup_handler)
        
    def update_folder_prefix(self):
        prefix = self.folder_prefix_le.text()
        self.prefix_example_lb.setText(
            f'  ex) {os.path.basename(self.target_le.text())} -> {prefix}_{os.path.basename(self.target_le.text())}'
            )
    
    def populate_data(self):
        node = nuke.selectedNode()
        file_path = node['file'].value()
        directory_path = os.path.dirname(file_path)
        self.files = sorted([f for f in os.listdir(directory_path) if f.endswith(self.sequence_ext_cmbx.currentText())])
        first_frame_path = os.path.join(directory_path, self.files[0]).replace(os.sep, '/')
        self.channels = []
        
        if not self.files:
            QMessageBox.warning(self, 'Warning', 'No sequence files found in the selected node path.')
            return

        temp_channels = self.get_image_channels(first_frame_path)
        if not temp_channels:
            QMessageBox.warning(self, 'Warning', 'Failed to retrieve channels from the first frame.')
            return
        
        for channel in temp_channels:
            if not '.' in channel:
                continue
            
            short_channel = channel.split('.')[0]
            if short_channel not in self.channels:
                self.channels.append(short_channel)
        
        self.selected_node_lb.setText(f'Selected Node: {node.name()}')
        self.target_le.setText(directory_path)
        self.export_log_le.setText(os.path.join(directory_path, 'channel_log.log').replace(os.sep, '/'))
        
        # Populate table
        for i, channel in enumerate(self.channels):
            self.table_widget.insertRow(i)
            
            # Set Render checkbox
            render_widget = QWidget()
            render_layout = QHBoxLayout(render_widget)
            render_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            render_layout.setContentsMargins(0, 0, 0, 0)
            render_ckbx = QCheckBox()
            render_ckbx.setChecked(True)
            render_layout.addWidget(render_ckbx)
            self.table_widget.setCellWidget(i, self.headers.index('Render'), render_widget)
            
            # Set channel name
            channel_item = QTableWidgetItem(channel)
            channel_item.setFlags(channel_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table_widget.setItem(i, self.headers.index('Channel'), channel_item)
            
            # Set Data Exists
            exists_item = QTableWidgetItem('N/A')
            exists_item.setFlags(exists_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            exists_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(i, self.headers.index('Data Exists'), exists_item)
        
    def get_image_channels(self, file_path):
        try:
            read = nuke.createNode("Read", inpanel=False)
            read['file'].fromUserText(file_path)
            channels = read.channels()

            # TODO: Add filtering options if needed
            channels_filter = ['N.', 'albedo.', 'normal.']

            filtered_channels = [
                ch for ch in channels
                if not any(ch.startswith(excluded) for excluded in channels_filter)
            ]
            nuke.delete(read)
            return list(filtered_channels)
        except Exception as e:
            print(traceback.format_exc())
            QMessageBox.warning(self, 'Warning', 'Error retrieving channels from EXR file.')
            return []
        
    def show_context_menu(self, pos):
        self.table_menu = QMenu()
        
        # Actions
        self.check_selected_action = self.table_menu.addAction("Check Selected")
        self.uncheck_selected_action = self.table_menu.addAction("Uncheck Selected")
        self.table_menu.addSeparator()
        self.check_all_action = self.table_menu.addAction("Check All")
        self.uncheck_all_action = self.table_menu.addAction("Uncheck All")
        
        action = self.table_menu.exec_(self.table_widget.mapToGlobal(pos))
        if action == self.check_selected_action:
            self.check_selected()
        elif action == self.uncheck_selected_action:
            self.uncheck_selected()
        elif action == self.check_all_action:
            self.check_all()
        elif action == self.uncheck_all_action:
            self.uncheck_all()

    def analyze_handler(self):
        frame_step = self.frame_step_sb.value()
        directory_path = self.target_le.text()
        export_log = self.log_group.isChecked()
        log_path = self.export_log_le.text()
        start_time = time.time()
        
        if not os.path.exists(directory_path):
            QMessageBox.warning(self, 'Warning', f'Path does not exist: {directory_path}')
            return
        
        if export_log and not log_path:
            QMessageBox.warning(self, 'Warning', 'Please specify a log file path.')
            return
        
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        try:
            valid_channels, empty_channels, channel_first_seen = self.analyze_sequence()
        except Exception as e:
            print(traceback.format_exc())
            QMessageBox.warning(self, 'Warning', 'An error occurred during analysis.')
            return
        
        if not valid_channels and not empty_channels:
            QMessageBox.warning(self, 'Warning', 'No analysis results found.')
            return
        
        for row in range(self.table_widget.rowCount()):
            channel = self.table_widget.item(row, self.headers.index('Channel')).text()
            render = self.table_widget.cellWidget(row, self.headers.index('Render'))
            ckbx = render.findChild(QCheckBox)
            ckbx.setChecked(True if channel in valid_channels else False)
            item = QTableWidgetItem('O' if channel in valid_channels else 'X' if channel in empty_channels else 'N/A')
            item.setTextColor(
                QColor(0, 255, 0) if channel in valid_channels 
                else QColor(255, 0, 0) if channel in empty_channels 
                else QColor(0, 0, 0)
                )
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table_widget.setItem(row, self.headers.index('Data Exists'), item)
        
        if self.log_group.isChecked():
            with open(log_path, 'w') as f:
                f.write("[Empty Channels Analysis]\n")
                f.write(f"  - Directory: {directory_path}\n")
                f.write(f"  - Frame Step: {frame_step}\n")
                f.write(f"  - Elapsed Time: {time.time() - start_time:.2f} seconds\n\n")
                f.write(f"[Valid Channels]: {valid_channels}\n\n")
                f.write(f"[Empty Channels]: {empty_channels}\n\n")
                f.write("[Valid Channels Data]\n")
                f.write(pprint.pformat(channel_first_seen))

            QMessageBox.information(self, 'Information', 'Analysis and log creation completed.')
            self.setup_btn.setEnabled(True)
        else:
            QMessageBox.information(self, 'Information', 'Analysis completed.')
            self.setup_btn.setEnabled(True)
    
    def _get_unchecked_rows(self):
        unchecked_rows = []
        for row in range(self.table_widget.rowCount()):
            render = self.table_widget.cellWidget(row, self.headers.index("Render"))
            ckbx = render.findChild(QCheckBox)
            if not ckbx.isChecked():
                unchecked_rows.append(row)
        return unchecked_rows
    
    def setup_handler(self):
        unchecked_rows = self._get_unchecked_rows()
        nk_template_path = os.path.join(os.path.dirname(__file__), 'OIDN_Converter.nk')
        if not os.path.exists(nk_template_path):
            QMessageBox.warning(self, 'Warning', 'Template file not found.')
            return
        
        nk_template = nuke.nodePaste(nk_template_path)
        if not nk_template:
            QMessageBox.warning(self, 'Warning', 'Failed to load template file.')
            return
        
        read_node = nuke.toNode(self.selected_node.name())
        origin_basename = os.path.basename(read_node['file'].value())
        nk_template.setInput(0, read_node)
        nk_template['xpos'].setValue(read_node['xpos'].value())
        nk_template['ypos'].setValue(read_node['ypos'].value() + 100)
        
        write_node = nuke.createNode('Write')
        write_node.setInput(0, nk_template)
        write_node['channels'].setValue('all')
        write_node['colorspace'].setValue('ACES - ACEScg')
        write_node['xpos'].setValue(nk_template['xpos'].value())
        write_node['ypos'].setValue(nk_template['ypos'].value() + 50)
        
        target_path = self.target_le.text()
        basename = os.path.basename(target_path)
        folder_path = '/'.join(target_path.split('/')[0:-1])
        folder_path = os.path.join(folder_path, f"{self.folder_prefix_le.text()}_{basename}").replace(os.sep, '/')
        
        origin_basename = origin_basename.replace(basename, f"{self.folder_prefix_le.text()}_{basename}")
        
        write_node['file'].setValue(os.path.join(folder_path, origin_basename).replace(os.sep, '/'))
        
        os.makedirs(folder_path, exist_ok=True)
        
        if unchecked_rows:
            self.disable_shuffles(nk_template, unchecked_rows)
            
        write_node.setSelected(True)
        
        if self.run_submitter_cmbx.currentText() == 'Submit':
            # TODO: Integrate DeadlineNukeClient if available
            # DeadlineNukeClient.main()
            pass
        else:
            QMessageBox.information(self, 'Information', '노드 설정이 완료되었습니다.')
        
    def disable_shuffles(self, nk_template, unchecked_rows):
        shuffle_nodes = {}
        nk_template.begin()
        try:
            all_nodes = nuke.allNodes()
        finally:
            nk_template.end()
            
        for node in all_nodes:
            if not node.Class() == 'Shuffle2':
                continue
            
            label = node['label'].value()
            if not label.startswith('OIDN'):
                continue
            
            label_split = label.split('\n')[-1]
            shuffle_nodes[label_split] = node
            
        for row in unchecked_rows:
            channel = self.table_widget.item(row, self.headers.index('Channel')).text()
            shuffle_node = shuffle_nodes.get(channel)
            if not shuffle_node:
                continue
            
            shuffle_node['disable'].setValue(True)
                
    def validate_exr_channels(self, node, frame_number, target_channels):
        empty_channels = []
        valid_channels = []

        shuffle = nuke.createNode('Shuffle', inpanel=False)
        shuffle['xpos'].setValue(0)
        shuffle['ypos'].setValue(50)
        shuffle.setInput(0, node)
        curve_tool = nuke.createNode('CurveTool', inpanel=False)
        curve_tool['xpos'].setValue(0)
        curve_tool['ypos'].setValue(100)
        w, h = curve_tool.width(), curve_tool.height()

        for channel in target_channels:
            shuffle['in'].setValue(channel)
            curve_tool['operation'].setValue('Max Luma Pixel')
            curve_tool['ROI'].setValue((0, 0, w, h))
            nuke.execute(curve_tool, frame_number, frame_number)
            max_data = curve_tool['maxlumapixvalue'].value()
            min_data = curve_tool['minlumapixvalue'].value()
            max_val = max(max_data)
            min_val = max(min_data)

            if max_val == 0 and min_val == 0:
                empty_channels.append(channel)
            else:
                valid_channels.append(channel)

        nuke.delete(curve_tool)
        nuke.delete(shuffle)

        return valid_channels, empty_channels
    
    def browse_log_path(self):
        default_path = os.path.dirname(self.export_log_le.text()) if self.export_log_le.text() else os.path.expanduser("~")
        log_path, _ = QFileDialog.getSaveFileName(self, 'Save Log File', default_path, 'Log Files (*.log)')
        if log_path:
            self.export_log_le.setText(log_path)

    def analyze_sequence(self):
        directory_path = self.target_le.text()
        frame_step = self.frame_step_sb.value()
        
        initial_channels = self.channels

        remaining_channels = initial_channels[:]
        channel_status = {ch: True for ch in initial_channels}
        channel_first_seen = {}
        
        for i, file_name in enumerate(self.files):
            if not i % frame_step == 0:
                continue

            frame_path = os.path.join(directory_path, file_name).replace(os.sep, '/')
            if not os.path.exists(frame_path):
                print(f"File not found: {frame_path}")
                continue

            node = nuke.createNode("Read", f"file {{{frame_path}}}", inpanel=False)
            node['xpos'].setValue(0)
            node['ypos'].setValue(0)
            frame_number = int(os.path.splitext(file_name)[0][-4:])

            valid_channels, empty_channels = self.validate_exr_channels(node, frame_number, remaining_channels)

            for ch in valid_channels:
                if ch not in channel_first_seen:
                    channel_first_seen[ch] = frame_number
            for ch in valid_channels:
                channel_status[ch] = False

            remaining_channels = [ch for ch in remaining_channels if channel_status[ch]]
            nuke.delete(node)

            if not remaining_channels:
                break
            
        empty_channels = [ch for ch, is_empty in channel_status.items() if is_empty]
        valid_channels = [ch for ch, is_empty in channel_status.items() if not is_empty]

        return valid_channels, empty_channels, channel_first_seen
            
    def check_selected(self):
        selected = self.table_widget.selectedIndexes()
        for item in selected:
            render = self.table_widget.cellWidget(item.row(), self.headers.index("Render"))
            ckbx = render.findChild(QCheckBox)
            ckbx.setChecked(True)

    def uncheck_selected(self):
        selected = self.table_widget.selectedIndexes()
        for item in selected:
            render = self.table_widget.cellWidget(item.row(), self.headers.index("Render"))
            ckbx = render.findChild(QCheckBox)
            ckbx.setChecked(False)
    
    def check_all(self):
        for row in range(self.table_widget.rowCount()):
            render = self.table_widget.cellWidget(row, self.headers.index("Render"))
            ckbx = render.findChild(QCheckBox)
            ckbx.setChecked(True)

    def uncheck_all(self):
        for row in range(self.table_widget.rowCount()):
            render = self.table_widget.cellWidget(row, self.headers.index("Render"))
            ckbx = render.findChild(QCheckBox)
            ckbx.setChecked(False)
            
            
def main():
    app = QApplication.instance()
    if not app:
        raise RuntimeError("No Qt Application found.")
    
    try:
        selected_node = nuke.selectedNode()
    except ValueError:
        QMessageBox.warning(None, 'Warning', 'Please select a node.')
        return
    
    if not selected_node.Class() == 'Read':
        QMessageBox.warning(None, 'Warning', 'The selected node is not a Read node.')
        return
    
    if not selected_node['file']:
        QMessageBox.warning(None, 'Warning', 'The selected node does not have a file specified.')
        return
    global channelChecker
    channelChecker = ChannelChecker(selected_node)
