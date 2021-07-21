/*
 * Copyright (C) 2008-2010 Martin Riesz <riesz.martin at gmail.com>
 * Copyright (C) 2016-2017 Joaquin Rodriguez Felici <joaquinfelici at gmail.com>
 * Copyright (C) 2016-2017 Leandro Asson <leoasson at gmail.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

package org.petrinator.editor.actions.algorithms;

import com.google.gson.Gson;
import org.petrinator.editor.Root;
import org.petrinator.editor.actions.ReloadFileAction;
import org.petrinator.editor.filechooser.*;
import org.petrinator.petrinet.*;
import org.petrinator.util.GraphicsTools;
import org.petrinator.util.Print;
import org.petrinator.util.Save;

import pipe.gui.widgets.ButtonBar;
import pipe.gui.widgets.EscapableDialog;
import pipe.gui.widgets.ResultsHTMLPane;
import pipe.utilities.math.Matrix;
import javax.swing.*;
import java.awt.*;
import java.util.*;
import java.net.*;
import java.io.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.List;

public class AutomaticPolitics extends AbstractAction
{
    private static final String MODULE_NAME = "Automatics Politics";
    private ResultsHTMLPane results;
    private String sPanel;
    private Root root;
    private JDialog guiDialog;
    private ButtonBar FirstAnalizeButton;
    private ButtonBar showPlotButton;
    private ButtonBar HelpButton;
    String[] cost = {"simp", "inv"};
    JComboBox tipoCosto = new JComboBox(cost);
    JTextField firenumbers = new JTextField(0);
    JTextField repeats = new JTextField(0);
    JCheckBox netWithMod = new JCheckBox("NET with Modifications" );
    JCheckBox netWithControlPlaces = new JCheckBox("NET with Control Places");

    JCheckBox modifyNetButton = new JCheckBox("Modify NET" );
    InvariantAction accion;
    MatricesAction matrices;

    public AutomaticPolitics(Root root)
    {
        this.root = root;
        putValue(NAME, MODULE_NAME);
        putValue(SHORT_DESCRIPTION, MODULE_NAME);
        putValue(SMALL_ICON, GraphicsTools.getIcon("pneditor/politicsIconx16.png"));

        guiDialog =  new JDialog(root.getParentFrame(), MODULE_NAME, true);
        guiDialog.setModalityType(Dialog.ModalityType.MODELESS);
        Container contentPane = guiDialog.getContentPane();
        contentPane.setLayout(new BoxLayout(contentPane, BoxLayout.PAGE_AXIS));
        results = new ResultsHTMLPane("");
        sPanel = new String();//new
        contentPane.add(results);
        FirstAnalizeButton = new ButtonBar("Run Politics Analysis", new RunListener(), guiDialog.getRootPane());
        showPlotButton = new ButtonBar("Show Plot", new showPlotListener(), guiDialog.getRootPane());
        HelpButton = new ButtonBar("Help", new HelpListener(), guiDialog.getRootPane());
        //action listener del plazas de control
        //netWithControlPlaces.addActionListener(new PlaceControlListener());
        //
        JPanel checkPanel = new JPanel(new GridLayout(3,3));
        //agrego al nuevo panel
        //String[] cost = {"simp", "inv"};
        //JComboBox tipoCosto = new JComboBox(cost);
        checkPanel.add(new JLabel("Firenumber:"),BorderLayout.PAGE_START);
        checkPanel.add(firenumbers,BorderLayout.PAGE_START);
        checkPanel.add(netWithControlPlaces);
        checkPanel.add(new JLabel("Repeat:"));
        checkPanel.add(repeats);
        checkPanel.add(modifyNetButton);
        checkPanel.add(new JLabel("Cost type:"));
        checkPanel.add(tipoCosto);
        checkPanel.add(netWithMod);
        //termino de agregar al nuevo panel
        contentPane.add(checkPanel, BorderLayout.CENTER);
        JPanel checkPanel2 = new JPanel(new GridLayout(1,2));
        checkPanel2.add(FirstAnalizeButton);
        checkPanel2.add(showPlotButton);
        contentPane.add(checkPanel2, BorderLayout.CENTER);
        contentPane.add(HelpButton);
        //creo un objeto de invariantes
        accion = new InvariantAction(this.root);
        matrices = new MatricesAction(this.root);
        //sifon = new SiphonsAction(this.root);

    }


    public void actionPerformed(ActionEvent e)
    {
        if(!root.getDocument().getPetriNet().getRootSubnet().isValid())
        {
            results.setText("Invalid Net");
            JOptionPane.showMessageDialog(null, "Invalid Net!", "Error analysing net", JOptionPane.ERROR_MESSAGE, null);
            guiDialog.setVisible(false);
            //close_socket();
            return;
        }
        results.setText("");

        // Disables the copy and save buttons
        results.setEnabled(false);

        // Enables classify button
        FirstAnalizeButton.setButtonsEnabled(true);
        FirstAnalizeButton.setEnabled(true);//para luego chequear
        showPlotButton.setButtonsEnabled(false);
        ArrayList<String> controlPlaces = root.getDocument().getPetriNet().getControlPlaces();
        ArrayList<String> Update_transitions = root.getDocument().getPetriNet().getUpdateTArray();

        if(controlPlaces.isEmpty())
        {
            netWithControlPlaces.setSelected(false);
        }
        else
        {
            netWithControlPlaces.setToolTipText(controlPlaces.toString());
            netWithControlPlaces.setSelected(true);
        }


        if(Update_transitions.isEmpty())
        {
            netWithMod.setSelected(false);
        }
        else
        {
            netWithMod.setToolTipText(Update_transitions.toString());
            netWithMod.setSelected(true);
        }

        //print_arraylistStringonly(controlPlaces,"plazas de control");
        netWithControlPlaces.setEnabled(false);
        netWithMod.setEnabled(false);
        // Shows initial pane
        guiDialog.pack();
        guiDialog.setLocationRelativeTo(root.getParentFrame());
        guiDialog.setVisible(true);
    }

    private String getInputAsString(InputStream is)
    {
        try(java.util.Scanner s = new java.util.Scanner(is))
        {
            return s.useDelimiter("\\A").hasNext() ? s.next() : "";
        }
    }
    private int execPolitics()
    {
        sPanel = "<h2>Run Automatic Politics Analisys</h2>";
        List<String> comandos = new ArrayList<String>();

        try {
            comandos.add("python3");//1°comand
            //Get tesis python path and execute
            String  jar_path = Save.get_Current_JarPath(AutomaticPolitics.class,root,results);
            String pathToPythonMain;
            if(jar_path!= null)pathToPythonMain = jar_path +"/Modulos/Automatic-politics/main.py";
            else return 1;
            comandos.add(pathToPythonMain);//2°comand
            comandos.add("./Modulos/Automatic-politics/tmp/jsonmat.json");//3°comand
            try
            {
                if(0 >= Integer.valueOf(firenumbers.getText()) || Integer.valueOf(firenumbers.getText())>100000)
                {
                    JOptionPane.showMessageDialog(null, "Invalid range of firenumbers");
                    return 1;
                }
                comandos.add("-n");//4°comand
                comandos.add(firenumbers.getText());//5°comand
                if(0 >= Integer.valueOf(repeats.getText()) || Integer.valueOf(repeats.getText())>10)
                {
                    JOptionPane.showMessageDialog(null, "Invalid range of repeats");
                    return 1;
                }
                comandos.add("-r");//6°comand
                comandos.add(repeats.getText());//7°comand
                comandos.add("-t");//8°comand
                comandos.add(tipoCosto.getSelectedItem().toString());//9°comand
                if(netWithMod.isSelected())
                {
                    comandos.add("-l");

                }
                if(modifyNetButton.isSelected())
                {
                    comandos.add("-m");
                    comandos.add(root.getCurrentFile().getPath());
                }

            } catch (NumberFormatException e) {
                JOptionPane.showMessageDialog(null, "Invalid firenumber or repeats");
                return 1;
            }
            Print.print_arraylist_string((ArrayList<String>) comandos,"comando");
            ProcessBuilder pb = new ProcessBuilder(comandos);
            pb.redirectErrorStream(true);
            sPanel+= getInputAsString(pb.start().getInputStream());
            results.setText(sPanel);
            Save.reSaveNet(root);
            //showPlot();

        } catch (IOException e) {
            results.setText("");
            e.printStackTrace();
            JOptionPane.showMessageDialog(root.getParentFrame(),e.getMessage(), "Error executing python module", JOptionPane.ERROR_MESSAGE);
            return 1;
        }
        return 0;
    }

    /**
     * hace el analisis de t invariantes
     * @return Array list con T invariantes de a forma [T1,T2,T3]
     */
    public ArrayList<String[]> invariantAnalysis()
    {
        ArrayList<String> TinvariantsLabels_aux=new ArrayList<String>();
        ArrayList<String[]> TinvariantsLabels=new ArrayList<String[]>();
        Matrix TInvariants = accion.findVectors(new Matrix(root.getDocument().getPetriNet().getIncidenceMatrix()));
        ArrayList<String> transNames = root.getDocument().getPetriNet().getSortedTransitionsNames();
        for (int c=0; c < TInvariants.getColumnDimension(); c++)
        {
            //System.out.println("Fila: "+(f+1));
            TinvariantsLabels_aux.add(new String());
            for (int f=0; f < TInvariants.getRowDimension(); f++)
            {
                if(TInvariants.get(f,c)==1)
                {
                    TinvariantsLabels_aux.set(c,TinvariantsLabels_aux.get(c)+transNames.get(f)+" ");
                }
            }
            TinvariantsLabels.add(TinvariantsLabels_aux.get(c).split(" "));
        }
        return TinvariantsLabels;
    }

    /**
     * exporta los json files que utilitizara el agortimo .json (todas las matrices) y cfg.json
     * (costos estaticos y T-Invariantes)
     * @return 1 en caso de error , 0 caso exitoso
     */
    public int exportJsonsFiles()
    {
        Map<String, Object> extraAttributes = new HashMap<>();
        ArrayList<String> controlPlaces = root.getDocument().getPetriNet().getControlPlaces();
        ArrayList<String> Update_Transitions = root.getDocument().getPetriNet().getUpdateTArray();
        Gson gson = new Gson();
        extraAttributes.put("Costos", root.getDocument().getPetriNet().getCostArray());
        extraAttributes.put("Invariantes",invariantAnalysis());
        
        if(!controlPlaces.isEmpty())
        {
            extraAttributes.put("ControlPlaces",controlPlaces);
        }
        if(!Update_Transitions.isEmpty())
        {
            extraAttributes.put("UpdateT",Update_Transitions);
        }

        String json = gson.toJson(extraAttributes);

        String destFNcfg,destFN;
        String jar_path = Save.get_Current_JarPath(AutomaticPolitics.class,root,results);
        if(jar_path != null)destFNcfg = jar_path + "/Modulos/Automatic-politics/tmp/jsonmat.cfg.json";
        else return 1;

        try {
            FileWriter writer = new FileWriter(new File(destFNcfg));
            writer.write(json);
            writer.close();
        } catch (Exception var6) {
            System.out.println("Error saving CGF.JSON to file");
        }
        //only matrices
        if(jar_path != null)destFN = jar_path + "/Modulos/Automatic-politics/tmp/jsonmat.json";
        else return 1;
        Map<String, Object> matricesonly = new HashMap<>();

        Gson gsononly = new Gson();

        matricesonly.put("I-", root.getDocument().getPetriNet().getBackwardsIMatrix());
        matricesonly.put("I+", root.getDocument().getPetriNet().getForwardIMatrix());
        matricesonly.put("Incidencia", root.getDocument().getPetriNet().getIncidenceMatrix());
        matricesonly.put("Inhibicion", root.getDocument().getPetriNet().getInhibitionMatrix());
        matricesonly.put("Marcado", root.getDocument().getPetriNet().getInitialMarking().getMarkingAsArray()[Marking.CURRENT]);

        String jsononly = gsononly.toJson(matricesonly);
        try {
            FileWriter writer = new FileWriter(new File(destFN));
            writer.write(jsononly);
            writer.close();
        } catch (Exception var6) {
            System.out.println("Error saving JSON to file");
        }
        return 0;
    }
    private class showPlotListener implements ActionListener {
        public void actionPerformed(ActionEvent e) {
            /*
             * Create the dialog
             */
            EscapableDialog guiDialog = new EscapableDialog(root.getParentFrame(), "Plot results", false);
            Container contentPane = guiDialog.getContentPane();
            //org.petrinator.auxiliar.ResultsHTMLPane results = new org.petrinator.auxiliar.ResultsHTMLPane("");
            //contentPane.add(results);
            //
            File fichero=new File(Save.get_Current_JarPath(AutomaticPolitics.class,root,results) + "/plot.png");
            ImageIcon books = new ImageIcon(fichero.getPath());
            JLabel imgLabel = new JLabel();
            imgLabel.setIcon(books);
            imgLabel.setMaximumSize(new Dimension(books.getIconWidth(), books.getIconHeight()));
            imgLabel.setAutoscrolls(true);
            imgLabel.grabFocus();
            contentPane.add(imgLabel);
            //
            guiDialog.pack();
            guiDialog.setAlwaysOnTop(true);
            guiDialog.setLocationRelativeTo(root.getParentFrame());
            guiDialog.setVisible(true);

            //String s = "<img src='"+get_Current_JarPath()+"/plotonly.png"+"' class='img-responsive' height='1000' width='1200' alt=''>";

            System.out.println(fichero.getPath());
            books.getImage().flush();
        }
    }

    /**
     * Listener for analyse button
     */
    private class RunListener implements ActionListener {

        public void actionPerformed(ActionEvent actionEvent)
        {
            System.out.println("----- Running Politics Analysis -----");
            // Checks if the net is valid
            if(!root.getDocument().getPetriNet().getRootSubnet().isValid())
            {
                results.setText("Invalid Net");
                JOptionPane.showMessageDialog(null, "Invalid Net!", "Error analysing net", JOptionPane.ERROR_MESSAGE, null);
                guiDialog.setVisible(false);
                //close_socket();
                return;
            }
            exportJsonsFiles();
            execPolitics();
            results.setVisible(true);
            showPlotButton.setButtonsEnabled(true);
            
            ArrayList<String> Update_transitions = root.getDocument().getPetriNet().getUpdateTArray();
    
            if(Update_transitions.isEmpty())
            {
                netWithMod.setSelected(false);
            }
            else
            {
                netWithMod.setToolTipText(Update_transitions.toString());
                netWithMod.setSelected(true);
            }

        }
    };
    private class HelpListener implements ActionListener {
        public void actionPerformed(ActionEvent e)
        {
            /*
             * Create the dialog
             */
            EscapableDialog guiDialog = new EscapableDialog(root.getParentFrame(), "Help: Automatics Politics", false);
            Container contentPane = guiDialog.getContentPane();
            org.petrinator.auxiliar.ResultsHTMLPane results = new org.petrinator.auxiliar.ResultsHTMLPane("");
            contentPane.add(results);
            guiDialog.pack();
            guiDialog.setAlwaysOnTop(true);
            guiDialog.setLocationRelativeTo(root.getParentFrame());
            guiDialog.setVisible(true);

            /*
             * Read the about.html file
             */
            InputStream aboutFile = getClass().getResourceAsStream("/AutomaticPoliticsHelp.html");
            Scanner scanner = null;
            scanner = new Scanner(aboutFile, "UTF-8");
            String s = scanner.useDelimiter("\\Z").next();
            scanner.close();

            /*
             * Show the text on dialog
             */
            results.setText(s);
        }
    };
  
}
